"""
Gap Analysis Service for Learning Pathway Completeness.
Identifies missing prerequisites and weak supporting content areas.
"""
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

from src.db.models.content import LearningContent, LearningPathway, PathwayItem
from src.services.vector_store import vector_store
from src.config import get_settings

settings = get_settings()

@dataclass
class GapAnalysis:
    """Result of gap analysis for a learning pathway or content domain."""
    pathway_id: Optional[int]
    target_persona: str
    end_goal: str
    gaps: List['ContentGap']
    pathway_strength: float  # 0-1 score
    total_missing_prerequisites: int
    weak_support_areas: List[str]
    # Weighted analysis fields
    weighted_gap_score: float = 0.0  # Overall weighted gap severity
    critical_gaps: List[str] = None  # Highest impact gaps
    gap_distribution: Dict[str, int] = None  # Gap counts by severity
    
    def __post_init__(self):
        if self.critical_gaps is None:
            self.critical_gaps = []
        if self.gap_distribution is None:
            self.gap_distribution = {}

@dataclass
class ContentGap:
    """Represents a specific gap in learning content."""
    gap_type: str  # 'missing_prerequisite' or 'weak_support'
    missing_concept: str
    current_content_id: Optional[int]
    prerequisite_for: str
    supporting_content_count: int
    average_duration: float
    average_difficulty: str
    similarity_scores: List[float]
    recommendations: List[str]
    # Weighted scoring fields
    outcome_weight: float = 0.0  # Impact on final learning outcome (0-1)
    path_distance: int = 0       # Steps from gap to learning goal
    dependency_depth: int = 0    # How many concepts depend on this
    gap_severity_score: float = 0.0  # Overall gap severity (0-1)

class GapAnalysisService:
    """Service for analyzing learning pathway gaps and content completeness."""
    
    def __init__(self):
        self.similarity_threshold = settings.SIMILARITY_THRESHOLD
        self.weak_support_threshold = 3  # Minimum supporting content items
    
    async def analyze_pathway_gaps(
        self,
        db: AsyncSession,
        pathway_id: int
    ) -> GapAnalysis:
        """Analyze gaps in a specific learning pathway."""
        
        # Get pathway with all content
        pathway = await self._get_pathway_with_content(db, pathway_id)
        if not pathway:
            raise ValueError(f"Pathway {pathway_id} not found")
        
        gaps = []
        total_missing = 0
        weak_areas = []
        
        # Build pathway context for weighted analysis
        pathway_context = {
            'pathway_id': pathway_id,
            'total_items': len(pathway.items),
            'target_persona': pathway.target_persona,
            'end_goal': pathway.name
        }
        
        # Analyze each content item in the pathway
        for item in sorted(pathway.items, key=lambda x: x.sequence):
            content_gaps = await self._analyze_content_prerequisites(
                db, item.content, pathway.target_persona, pathway_context
            )
            gaps.extend(content_gaps)
            
            # Count missing prerequisites
            missing_prereqs = [g for g in content_gaps if g.gap_type == 'missing_prerequisite']
            total_missing += len(missing_prereqs)
            
            # Identify weak support areas
            weak_support = [g for g in content_gaps if g.gap_type == 'weak_support']
            weak_areas.extend([g.missing_concept for g in weak_support])
        
        # Calculate pathway strength and weighted metrics
        pathway_strength = self._calculate_pathway_strength(pathway, gaps)
        weighted_gap_score = self._calculate_weighted_gap_score(gaps)
        critical_gaps = self._identify_critical_gaps(gaps)
        gap_distribution = self._calculate_gap_distribution(gaps)
        
        return GapAnalysis(
            pathway_id=pathway_id,
            target_persona=pathway.target_persona,
            end_goal=pathway.name,
            gaps=gaps,
            pathway_strength=pathway_strength,
            total_missing_prerequisites=total_missing,
            weak_support_areas=list(set(weak_areas)),
            weighted_gap_score=weighted_gap_score,
            critical_gaps=critical_gaps,
            gap_distribution=gap_distribution
        )
    
    async def analyze_domain_gaps(
        self,
        db: AsyncSession,
        persona: str,
        learning_objectives: List[str]
    ) -> GapAnalysis:
        """Analyze gaps in a general learning domain."""
        
        # Find all content matching the persona and objectives
        relevant_content = await self._find_domain_content(
            db, persona, learning_objectives
        )
        
        gaps = []
        total_missing = 0
        weak_areas = []
        
        # Build domain context for weighted analysis
        domain_context = {
            'domain_objectives': learning_objectives,
            'total_content': len(relevant_content),
            'target_persona': persona
        }
        
        # Analyze each piece of content
        for content in relevant_content:
            content_gaps = await self._analyze_content_prerequisites(
                db, content, persona, domain_context
            )
            gaps.extend(content_gaps)
            
            missing_prereqs = [g for g in content_gaps if g.gap_type == 'missing_prerequisite']
            total_missing += len(missing_prereqs)
            
            weak_support = [g for g in content_gaps if g.gap_type == 'weak_support']
            weak_areas.extend([g.missing_concept for g in weak_support])
        
        # Calculate domain strength and weighted metrics
        domain_strength = self._calculate_domain_strength(relevant_content, gaps)
        weighted_gap_score = self._calculate_weighted_gap_score(gaps)
        critical_gaps = self._identify_critical_gaps(gaps)
        gap_distribution = self._calculate_gap_distribution(gaps)
        
        return GapAnalysis(
            pathway_id=None,
            target_persona=persona,
            end_goal=f"Domain: {', '.join(learning_objectives)}",
            gaps=gaps,
            pathway_strength=domain_strength,
            total_missing_prerequisites=total_missing,
            weak_support_areas=list(set(weak_areas)),
            weighted_gap_score=weighted_gap_score,
            critical_gaps=critical_gaps,
            gap_distribution=gap_distribution
        )
    
    async def _analyze_content_prerequisites(
        self,
        db: AsyncSession,
        content: LearningContent,
        target_persona: str,
        pathway_context: Optional[Dict[str, Any]] = None
    ) -> List[ContentGap]:
        """Analyze prerequisites for a specific content item with weighted scoring."""
        
        gaps = []
        
        # Extract potential prerequisites from content and metadata
        potential_prereqs = await self._extract_prerequisites(content)
        
        for prereq_concept in potential_prereqs:
            # Find supporting content for this prerequisite
            supporting_content = await self._find_supporting_content(
                db, prereq_concept, target_persona, content.tier
            )
            
            # Calculate weighted scores
            dependency_depth = await self._calculate_dependency_depth(db, prereq_concept, content)
            path_distance = self._calculate_path_distance(content, pathway_context)
            
            # Determine if this is a gap
            if len(supporting_content) == 0:
                # Missing prerequisite - no supporting content found
                gap = ContentGap(
                    gap_type='missing_prerequisite',
                    missing_concept=prereq_concept,
                    current_content_id=content.id,
                    prerequisite_for=content.title,
                    supporting_content_count=0,
                    average_duration=0,
                    average_difficulty='unknown',
                    similarity_scores=[],
                    recommendations=[f"Create {content.tier} content for {prereq_concept}"],
                    dependency_depth=dependency_depth,
                    path_distance=path_distance
                )
                gap.outcome_weight = self._calculate_outcome_weight(gap)
                gap.gap_severity_score = self._calculate_gap_severity(gap)
                gaps.append(gap)
                
            elif len(supporting_content) < self.weak_support_threshold:
                # Weak support - insufficient supporting content
                avg_duration = sum(c['duration'] for c in supporting_content) / len(supporting_content)
                avg_difficulty = self._calculate_average_difficulty(supporting_content)
                similarity_scores = [c['similarity_score'] for c in supporting_content]
                
                gap = ContentGap(
                    gap_type='weak_support',
                    missing_concept=prereq_concept,
                    current_content_id=content.id,
                    prerequisite_for=content.title,
                    supporting_content_count=len(supporting_content),
                    average_duration=avg_duration,
                    average_difficulty=avg_difficulty,
                    similarity_scores=similarity_scores,
                    recommendations=[
                        f"Add more {content.tier} content for {prereq_concept}",
                        f"Improve existing content quality (avg similarity: {sum(similarity_scores)/len(similarity_scores):.2f})"
                    ],
                    dependency_depth=dependency_depth,
                    path_distance=path_distance
                )
                gap.outcome_weight = self._calculate_outcome_weight(gap)
                gap.gap_severity_score = self._calculate_gap_severity(gap)
                gaps.append(gap)
        
        return gaps
    
    async def _extract_prerequisites(self, content: LearningContent) -> List[str]:
        """Extract potential prerequisites from content metadata and description."""
        
        prerequisites = []
        
        # Use existing explicit prerequisites
        if content.prerequisites:
            prerequisites.extend([p.title for p in content.prerequisites])
        
        # Extract from learning objectives
        if content.learning_objectives:
            for objective in content.learning_objectives:
                # Use vector similarity to find related concepts
                similar_concepts = await self._find_related_concepts(objective)
                prerequisites.extend(similar_concepts)
        
        # Extract from description using vector similarity
        if content.description:
            description_concepts = await self._find_related_concepts(content.description)
            prerequisites.extend(description_concepts)
        
        return list(set(prerequisites))  # Remove duplicates
    
    async def _find_related_concepts(self, text: str) -> List[str]:
        """Use vector similarity to find related learning concepts."""
        
        # Query vector store for similar content
        similar_items = vector_store.find_similar_content(
            query_text=text,
            similarity_threshold=0.6,
            max_results=5,
            search_approved_only=True
        )
        
        # Extract learning objectives from similar content
        concepts = []
        for item in similar_items:
            if 'learning_objectives' in item:
                objectives = item.get('learning_objectives', [])
                if isinstance(objectives, list):
                    concepts.extend(objectives)
        
        return concepts[:3]  # Return top 3 related concepts
    
    async def _find_supporting_content(
        self,
        db: AsyncSession,
        concept: str,
        persona: str,
        max_tier: str
    ) -> List[Dict[str, Any]]:
        """Find content that supports learning a specific concept."""
        
        # Search vector store for content matching the concept
        similar_content = vector_store.find_similar_content(
            query_text=concept,
            metadata_filters={
                'personas': persona,
                'tier': max_tier
            },
            similarity_threshold=0.5,
            max_results=10,
            search_approved_only=True
        )
        
        # Enrich with database information
        supporting_content = []
        for item in similar_content:
            content_id = item.get('content_id')
            if content_id:
                # Get full content details from database
                content = await db.get(LearningContent, content_id)
                if content:
                    supporting_content.append({
                        'content_id': content_id,
                        'title': content.title,
                        'duration': content.estimated_duration,
                        'tier': content.tier,
                        'similarity_score': item.get('similarity_score', 0)
                    })
        
        return supporting_content
    
    async def _get_pathway_with_content(
        self,
        db: AsyncSession,
        pathway_id: int
    ) -> Optional[LearningPathway]:
        """Get pathway with all related content loaded."""
        
        query = select(LearningPathway).options(
            joinedload(LearningPathway.items).joinedload(PathwayItem.content)
        ).where(LearningPathway.id == pathway_id)
        
        result = await db.execute(query)
        return result.scalars().unique().first()
    
    async def _find_domain_content(
        self,
        db: AsyncSession,
        persona: str,
        learning_objectives: List[str]
    ) -> List[LearningContent]:
        """Find all content relevant to a learning domain."""
        
        # Build query for content matching persona and objectives
        query = select(LearningContent).where(
            LearningContent.personas.contains([persona])
        )
        
        result = await db.execute(query)
        all_content = result.scalars().all()
        
        # Filter by learning objectives using vector similarity
        relevant_content = []
        for content in all_content:
            for objective in learning_objectives:
                # Check if content is relevant to this objective
                content_text = f"{content.title} {content.description}"
                similar_items = vector_store.find_similar_content(
                    query_text=objective,
                    similarity_threshold=0.4,
                    max_results=1
                )
                
                if similar_items and similar_items[0].get('content_id') == content.id:
                    relevant_content.append(content)
                    break
        
        return relevant_content
    
    def _calculate_pathway_strength(
        self,
        pathway: LearningPathway,
        gaps: List[ContentGap]
    ) -> float:
        """Calculate overall strength score for a pathway (0-1)."""
        
        if not pathway.items:
            return 0.0
        
        total_items = len(pathway.items)
        missing_prereqs = len([g for g in gaps if g.gap_type == 'missing_prerequisite'])
        weak_support = len([g for g in gaps if g.gap_type == 'weak_support'])
        
        # Penalize missing prerequisites more heavily than weak support
        penalty = (missing_prereqs * 0.8 + weak_support * 0.3) / total_items
        strength = max(0.0, 1.0 - penalty)
        
        return round(strength, 3)
    
    def _calculate_domain_strength(
        self,
        content_items: List[LearningContent],
        gaps: List[ContentGap]
    ) -> float:
        """Calculate overall strength score for a domain (0-1)."""
        
        if not content_items:
            return 0.0
        
        total_items = len(content_items)
        missing_prereqs = len([g for g in gaps if g.gap_type == 'missing_prerequisite'])
        weak_support = len([g for g in gaps if g.gap_type == 'weak_support'])
        
        penalty = (missing_prereqs * 0.7 + weak_support * 0.4) / total_items
        strength = max(0.0, 1.0 - penalty)
        
        return round(strength, 3)
    
    def _calculate_average_difficulty(self, supporting_content: List[Dict[str, Any]]) -> str:
        """Calculate average difficulty tier from supporting content."""
        
        if not supporting_content:
            return 'unknown'
        
        tier_values = {'T1': 1, 'T2': 2, 'T3': 3, 'T4': 4}
        total_value = sum(tier_values.get(c.get('tier', 'T1'), 1) for c in supporting_content)
        avg_value = total_value / len(supporting_content)
        
        # Map back to tier
        if avg_value <= 1.5:
            return 'T1'
        elif avg_value <= 2.5:
            return 'T2'
        elif avg_value <= 3.5:
            return 'T3'
        else:
            return 'T4'
    
    async def _calculate_dependency_depth(self, db: AsyncSession, concept: str, content: LearningContent) -> int:
        """Calculate how many other concepts depend on this prerequisite."""
        # Find content that lists this concept as a prerequisite
        similar_content = vector_store.find_similar_content(
            query_text=concept,
            similarity_threshold=0.6,
            max_results=20,
            search_approved_only=True
        )
        
        # Count content that would be blocked by this gap
        dependent_count = 0
        for item in similar_content:
            if item.get('content_id') != content.id:  # Don't count self
                dependent_count += 1
        
        return min(dependent_count, 10)  # Cap at 10 for scoring
    
    def _calculate_path_distance(self, content: LearningContent, pathway_context: Optional[Dict[str, Any]]) -> int:
        """Calculate steps from this content to pathway end goal."""
        if not pathway_context:
            return 1
        
        total_items = pathway_context.get('total_items', 1)
        # Simple heuristic: higher tier content is typically closer to end goals
        tier_values = {'T1': 4, 'T2': 3, 'T3': 2, 'T4': 1}
        base_distance = tier_values.get(content.tier, 2)
        
        # Adjust based on pathway size
        if total_items > 5:
            base_distance += 1
        
        return max(1, base_distance)
    
    def _calculate_outcome_weight(self, gap: ContentGap) -> float:
        """Calculate how much this gap impacts final learning outcomes."""
        # Base weight factors
        gap_type_weight = 1.0 if gap.gap_type == 'missing_prerequisite' else 0.6
        dependency_weight = min(gap.dependency_depth / 10.0, 1.0)  # Normalize to 0-1
        distance_weight = max(0.2, 1.0 - (gap.path_distance / 10.0))  # Closer = higher weight
        
        # Combine weights (chain rule approximation)
        outcome_weight = gap_type_weight * (0.5 + 0.3 * dependency_weight + 0.2 * distance_weight)
        
        return min(1.0, outcome_weight)
    
    def _calculate_gap_severity(self, gap: ContentGap) -> float:
        """Calculate overall severity score for this gap."""
        # Combine multiple factors
        base_severity = 1.0 if gap.gap_type == 'missing_prerequisite' else 0.5
        
        # Adjust for supporting content quality
        if gap.similarity_scores:
            avg_similarity = sum(gap.similarity_scores) / len(gap.similarity_scores)
            quality_penalty = max(0, 1.0 - avg_similarity)
            base_severity += quality_penalty * 0.3
        
        # Weight by outcome impact
        severity = base_severity * gap.outcome_weight
        
        return min(1.0, severity)
    
    def _calculate_weighted_gap_score(self, gaps: List[ContentGap]) -> float:
        """Calculate overall weighted gap score for pathway."""
        if not gaps:
            return 0.0
        
        total_weighted_severity = sum(gap.gap_severity_score * gap.outcome_weight for gap in gaps)
        max_possible_score = len(gaps)  # If all gaps had severity=1.0 and weight=1.0
        
        return min(1.0, total_weighted_severity / max_possible_score) if max_possible_score > 0 else 0.0
    
    def _identify_critical_gaps(self, gaps: List[ContentGap]) -> List[str]:
        """Identify the most critical gaps based on weighted scoring."""
        # Sort by combined severity and outcome weight
        sorted_gaps = sorted(
            gaps, 
            key=lambda g: g.gap_severity_score * g.outcome_weight, 
            reverse=True
        )
        
        # Return top 5 most critical gap concepts
        return [gap.missing_concept for gap in sorted_gaps[:5]]
    
    def _calculate_gap_distribution(self, gaps: List[ContentGap]) -> Dict[str, int]:
        """Calculate distribution of gaps by severity level."""
        distribution = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        
        for gap in gaps:
            severity = gap.gap_severity_score
            if severity >= 0.8:
                distribution['critical'] += 1
            elif severity >= 0.6:
                distribution['high'] += 1
            elif severity >= 0.4:
                distribution['medium'] += 1
            else:
                distribution['low'] += 1
        
        return distribution

# Global instance
gap_analysis_service = GapAnalysisService()