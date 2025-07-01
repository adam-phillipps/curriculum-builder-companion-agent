"""
Gap Analyzer Agent for identifying learning pathway gaps and content completeness issues.
Integrates with the gap analysis service to provide agent-based gap detection.
"""
from typing import Dict, List, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.gap_analysis import gap_analysis_service, GapAnalysis
from src.agents.state import AgentState
from src.config import get_settings

settings = get_settings()

class GapAnalyzerAgent:
    """Agent for analyzing learning pathway gaps and providing recommendations."""
    
    def __init__(self):
        self.service = gap_analysis_service
    
    async def analyze_pathway(
        self,
        db: AsyncSession,
        pathway_id: int,
        state: Optional[AgentState] = None
    ) -> Dict[str, Any]:
        """Analyze gaps in a learning pathway and provide recommendations."""
        
        try:
            # Perform gap analysis
            analysis = await self.service.analyze_pathway_gaps(db, pathway_id)
            
            # Generate agent recommendations
            recommendations = self._generate_recommendations(analysis)
            
            # Update agent state if provided
            if state:
                state["analysis_results"] = {
                    "pathway_id": pathway_id,
                    "gaps_found": len(analysis.gaps),
                    "pathway_strength": analysis.pathway_strength,
                    "recommendations": recommendations
                }
            
            return {
                "analysis": analysis,
                "recommendations": recommendations,
                "priority_actions": self._prioritize_actions(analysis),
                "success": True
            }
            
        except Exception as e:
            error_msg = f"Gap analysis failed for pathway {pathway_id}: {str(e)}"
            if state:
                if "errors" not in state:
                    state["errors"] = []
                state["errors"].append(error_msg)
            
            return {
                "analysis": None,
                "recommendations": [],
                "priority_actions": [],
                "success": False,
                "error": error_msg
            }
    
    async def analyze_domain(
        self,
        db: AsyncSession,
        persona: str,
        learning_objectives: List[str],
        state: Optional[AgentState] = None
    ) -> Dict[str, Any]:
        """Analyze gaps in a learning domain and provide recommendations."""
        
        try:
            # Perform domain gap analysis
            analysis = await self.service.analyze_domain_gaps(
                db, persona, learning_objectives
            )
            
            # Generate agent recommendations
            recommendations = self._generate_recommendations(analysis)
            
            # Update agent state if provided
            if state:
                state["analysis_results"] = {
                    "persona": persona,
                    "objectives": learning_objectives,
                    "gaps_found": len(analysis.gaps),
                    "domain_strength": analysis.pathway_strength,
                    "recommendations": recommendations
                }
            
            return {
                "analysis": analysis,
                "recommendations": recommendations,
                "priority_actions": self._prioritize_actions(analysis),
                "success": True
            }
            
        except Exception as e:
            error_msg = f"Domain gap analysis failed for {persona}: {str(e)}"
            if state:
                if "errors" not in state:
                    state["errors"] = []
                state["errors"].append(error_msg)
            
            return {
                "analysis": None,
                "recommendations": [],
                "priority_actions": [],
                "success": False,
                "error": error_msg
            }
    
    def _generate_recommendations(self, analysis: GapAnalysis) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on weighted gap analysis."""
        
        recommendations = []
        
        # Sort gaps by severity score for prioritization
        sorted_gaps = sorted(analysis.gaps, key=lambda g: g.gap_severity_score, reverse=True)
        
        # Recommendations for missing prerequisites (weighted by severity)
        missing_prereqs = [g for g in sorted_gaps if g.gap_type == 'missing_prerequisite']
        if missing_prereqs:
            high_impact_prereqs = [g for g in missing_prereqs if g.outcome_weight >= 0.7]
            recommendations.append({
                "type": "missing_prerequisites",
                "priority": "critical" if high_impact_prereqs else "high",
                "title": f"Create {len(missing_prereqs)} missing prerequisite content items",
                "description": f"Critical gaps found in prerequisite knowledge for {analysis.target_persona}",
                "actions": [
                    f"Create {gap.missing_concept} content for {gap.prerequisite_for} (severity: {gap.gap_severity_score:.2f})"
                    for gap in missing_prereqs[:5]  # Top 5 most critical
                ],
                "impact": "critical" if high_impact_prereqs else "high",
                "weighted_impact": sum(g.outcome_weight for g in missing_prereqs[:5])
            })
        
        # Recommendations for weak support areas (weighted by severity)
        weak_support = [g for g in sorted_gaps if g.gap_type == 'weak_support']
        if weak_support:
            high_impact_weak = [g for g in weak_support if g.outcome_weight >= 0.5]
            recommendations.append({
                "type": "weak_support",
                "priority": "high" if high_impact_weak else "medium",
                "title": f"Strengthen {len(weak_support)} content areas",
                "description": f"Areas with insufficient supporting content for {analysis.target_persona}",
                "actions": [
                    f"Add content for {gap.missing_concept} (currently {gap.supporting_content_count} items, severity: {gap.gap_severity_score:.2f})"
                    for gap in weak_support[:5]
                ],
                "impact": "high" if high_impact_weak else "medium",
                "weighted_impact": sum(g.outcome_weight for g in weak_support[:5])
            })
        
        # Overall pathway strength recommendation (using weighted gap score)
        if analysis.pathway_strength < 0.7 or analysis.weighted_gap_score > 0.4:
            priority = "critical" if analysis.weighted_gap_score > 0.6 else "high" if analysis.pathway_strength < 0.5 else "medium"
            recommendations.append({
                "type": "pathway_strength",
                "priority": priority,
                "title": f"Improve pathway strength (strength: {analysis.pathway_strength:.1%}, weighted gaps: {analysis.weighted_gap_score:.1%})",
                "description": "Pathway has significant gaps that may impact learning effectiveness",
                "actions": [
                    f"Focus on {len(analysis.critical_gaps)} critical gaps first: {', '.join(analysis.critical_gaps[:3])}",
                    "Review content sequencing and dependencies",
                    "Consider adding intermediate content steps"
                ],
                "impact": priority,
                "gap_distribution": analysis.gap_distribution
            })
        
        return recommendations
    
    def _prioritize_actions(self, analysis: GapAnalysis) -> List[Dict[str, Any]]:
        """Prioritize actions based on weighted gap analysis results."""
        
        actions = []
        
        # Sort all gaps by combined severity and outcome weight
        sorted_gaps = sorted(
            analysis.gaps,
            key=lambda g: g.gap_severity_score * g.outcome_weight,
            reverse=True
        )
        
        # High priority: Top weighted missing prerequisites
        missing_prereqs = [g for g in sorted_gaps if g.gap_type == 'missing_prerequisite']
        for gap in missing_prereqs[:3]:  # Top 3 most critical
            priority_score = gap.gap_severity_score * gap.outcome_weight
            actions.append({
                "priority": 1,
                "action": "create_content",
                "concept": gap.missing_concept,
                "target_persona": analysis.target_persona,
                "prerequisite_for": gap.prerequisite_for,
                "estimated_effort": "high" if gap.dependency_depth > 5 else "medium",
                "impact": "critical" if priority_score > 0.8 else "high",
                "severity_score": gap.gap_severity_score,
                "outcome_weight": gap.outcome_weight,
                "dependency_depth": gap.dependency_depth
            })
        
        # Medium priority: Top weighted weak support areas
        weak_support = [g for g in sorted_gaps if g.gap_type == 'weak_support']
        
        for gap in weak_support[:3]:
            priority_score = gap.gap_severity_score * gap.outcome_weight
            actions.append({
                "priority": 2,
                "action": "improve_content",
                "concept": gap.missing_concept,
                "target_persona": analysis.target_persona,
                "current_count": gap.supporting_content_count,
                "estimated_effort": "medium" if gap.dependency_depth <= 3 else "high",
                "impact": "high" if priority_score > 0.6 else "moderate",
                "severity_score": gap.gap_severity_score,
                "outcome_weight": gap.outcome_weight,
                "avg_similarity": sum(gap.similarity_scores) / len(gap.similarity_scores) if gap.similarity_scores else 0
            })
        
        return actions

# Global instance
gap_analyzer_agent = GapAnalyzerAgent()