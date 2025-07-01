"""
Pydantic schemas for gap analysis API endpoints.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class ContentGapSchema(BaseModel):
    """Schema for individual content gaps."""
    gap_type: str = Field(..., description="Type of gap: 'missing_prerequisite' or 'weak_support'")
    missing_concept: str = Field(..., description="The missing or weak concept")
    current_content_id: Optional[int] = Field(None, description="ID of content that needs this prerequisite")
    prerequisite_for: str = Field(..., description="What this concept is a prerequisite for")
    supporting_content_count: int = Field(..., description="Number of supporting content items found")
    average_duration: float = Field(..., description="Average duration of supporting content")
    average_difficulty: str = Field(..., description="Average difficulty tier of supporting content")
    similarity_scores: List[float] = Field(default_factory=list, description="Similarity scores of supporting content")
    recommendations: List[str] = Field(default_factory=list, description="Recommended actions to address gap")
    # Weighted scoring fields
    outcome_weight: float = Field(0.0, description="Impact on final learning outcome (0-1)")
    path_distance: int = Field(0, description="Steps from gap to learning goal")
    dependency_depth: int = Field(0, description="How many concepts depend on this")
    gap_severity_score: float = Field(0.0, description="Overall gap severity (0-1)")

class GapAnalysisSchema(BaseModel):
    """Schema for complete gap analysis results."""
    pathway_id: Optional[int] = Field(None, description="ID of analyzed pathway (null for domain analysis)")
    target_persona: str = Field(..., description="Target learner persona")
    end_goal: str = Field(..., description="Learning pathway or domain goal")
    gaps: List[ContentGapSchema] = Field(default_factory=list, description="Identified content gaps")
    pathway_strength: float = Field(..., description="Overall pathway strength score (0-1)")
    total_missing_prerequisites: int = Field(..., description="Total number of missing prerequisites")
    weak_support_areas: List[str] = Field(default_factory=list, description="Areas with weak content support")
    # Weighted analysis fields
    weighted_gap_score: float = Field(0.0, description="Overall weighted gap severity (0-1)")
    critical_gaps: List[str] = Field(default_factory=list, description="Highest impact gaps")
    gap_distribution: Dict[str, int] = Field(default_factory=dict, description="Gap counts by severity level")

class PathwayGapAnalysisRequest(BaseModel):
    """Request schema for pathway gap analysis."""
    pathway_id: int = Field(..., description="ID of the learning pathway to analyze")

class DomainGapAnalysisRequest(BaseModel):
    """Request schema for domain gap analysis."""
    persona: str = Field(..., description="Target learner persona")
    learning_objectives: List[str] = Field(..., description="Learning objectives to analyze")

class LearnerProfileSchema(BaseModel):
    """Schema for learner skill profile (future enhancement)."""
    persona: str = Field(..., description="Primary learner persona")
    skill_assessments: Dict[str, float] = Field(default_factory=dict, description="Skill area -> proficiency (0-1)")
    learning_preferences: Dict[str, Any] = Field(default_factory=dict, description="Learning style preferences")
    time_constraints: Optional[int] = Field(None, description="Available learning time per week (hours)")
    experience_level: str = Field("beginner", description="Overall experience level")

class PersonalizedGapAnalysisRequest(BaseModel):
    """Request schema for personalized gap analysis (future enhancement)."""
    pathway_id: Optional[int] = Field(None, description="Pathway ID (null for domain analysis)")
    learning_objectives: Optional[List[str]] = Field(None, description="Learning objectives for domain analysis")
    learner_profile: LearnerProfileSchema = Field(..., description="Learner's skill profile")

class GapAnalysisSummary(BaseModel):
    """Summary schema for gap analysis results."""
    total_pathways_analyzed: int
    total_gaps_found: int
    missing_prerequisites: int
    weak_support_areas: int
    average_pathway_strength: float
    average_weighted_gap_score: float
    top_missing_concepts: List[str]
    recommendations_by_priority: List[str]
    critical_gap_distribution: Dict[str, int]