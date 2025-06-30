from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
from src.config import BuilderConstants

class BaseSchema(BaseModel):
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class AssessmentQuestionBase(BaseSchema):
    difficulty_tier: str = Field(..., description="Difficulty tier (T1-T4)")
    knowledge_area: str
    subtopics: Optional[List[str]] = []
    personas: List[str]
    weight: float = Field(default=1.0, gt=0, le=10)
    is_active: bool = True
    question_type: str
    usage_count: int = 0
    success_rate: Optional[float] = None

    @validator('difficulty_tier')
    def validate_tier(cls, v):
        if v not in BuilderConstants.TIERS.get_names():
            raise ValueError(f"Invalid tier. Must be one of {BuilderConstants.TIERS.get_names()}")
        return v

    @validator('personas')
    def validate_personas(cls, v):
        valid_personas = BuilderConstants.PERSONAS.get_names()
        for persona in v:
            if persona not in valid_personas:
                raise ValueError(f"Invalid persona. Must be one of {valid_personas}")
        return v

class AssessmentQuestionCreate(AssessmentQuestionBase):
    question_text: str
    options: Optional[Dict[str, Any]] = None
    correct_answer: str
    test_cases: Optional[Dict[str, Any]] = None
    solution_template: Optional[str] = None
    hints: Optional[List[str]] = None
    explanation: Optional[str] = None
    validation_rules: Optional[Dict[str, Any]] = None

class AssessmentQuestionResponse(AssessmentQuestionBase):
    id: int
    created_at: datetime
    updated_at: datetime
    analytics: Optional[Dict[str, Any]] = None
    related_content: List['LearningContentResponse']

class LearningContentBase(BaseSchema):
    code_title: str = Field(..., pattern=r"T[1-4]\.[A-Z]{3}\.\d{3}")
    title: str
    description: str
    content_type: str
    tier: str
    personas: List[str]
    learning_objectives: List[str]
    estimated_duration: int = Field(..., gt=0)
    sandbox_type: str
    aws_services: Optional[List[str]] = None
    technical_requirements: Optional[Dict[str, Any]] = None
    estimated_cost: float = Field(default=0.0, ge=0)
    cost_breakdown: Optional[Dict[str, Any]] = None
    status: str = Field(default=BuilderConstants.STATES.DRAFT.name)
    tags: Optional[List[str]] = None
    notes: Optional[str] = None

    @validator('content_type')
    def validate_content_type(cls, v):
        if v not in BuilderConstants.CONTENT_TYPES.get_names():
            raise ValueError(f"Invalid content type. Must be one of {BuilderConstants.CONTENT_TYPES.get_names()}")
        return v

    @validator('tier')
    def validate_tier(cls, v):
        if v not in BuilderConstants.TIERS.get_names():
            raise ValueError(f"Invalid tier. Must be one of {BuilderConstants.TIERS.get_names()}")
        return v

    @validator('sandbox_type')
    def validate_sandbox_type(cls, v):
        if v not in BuilderConstants.SANDBOX_TYPES.get_names():
            raise ValueError(f"Invalid sandbox type. Must be one of {BuilderConstants.SANDBOX_TYPES.get_names()}")
        return v

    @validator('personas')
    def validate_personas(cls, v):
        valid_personas = BuilderConstants.PERSONAS.get_names()
        for persona in v:
            if persona not in valid_personas:
                raise ValueError(f"Invalid persona. Must be one of {valid_personas}")
        return v
class LearningContentCreate(LearningContentBase):
    prerequisite_ids: Optional[List[int]] = None
    assessment_question_ids: Optional[List[int]] = None

class LearningContentResponse(LearningContentBase):
    id: int
    created_at: datetime
    updated_at: datetime
    created_by: str
    updated_by: Optional[str] = None
    version: str
    prerequisites: List['LearningContentBase']
    assessment_questions: List[AssessmentQuestionBase]
    review_status: Optional[Dict[str, Any]] = None

class PricingEstimateBase(BaseSchema):
    estimate_type: str
    currency: str = "USD"
    compute_cost: float = Field(default=0.0, ge=0)
    storage_cost: float = Field(default=0.0, ge=0)
    network_cost: float = Field(default=0.0, ge=0)
    managed_services_cost: float = Field(default=0.0, ge=0)
    other_costs: float = Field(default=0.0, ge=0)
    cost_factors: Optional[Dict[str, Any]] = None
    assumptions: Optional[Dict[str, Any]] = None

class PricingEstimateCreate(PricingEstimateBase):
    content_id: int

class PricingEstimateResponse(PricingEstimateBase):
    id: int
    created_at: datetime
    updated_at: datetime
    content: LearningContentBase

class PathwayItemBase(BaseSchema):
    sequence: int = Field(..., ge=1)

class PathwayItemCreate(PathwayItemBase):
    content_id: int

class PathwayItemResponse(PathwayItemBase):
    id: int
    content: LearningContentBase

class LearningPathwayBase(BaseSchema):
    name: str
    description: Optional[str] = None
    target_persona: str
    estimated_duration: int
    total_cost: float = Field(default=0.0, ge=0)

    @validator('target_persona')
    def validate_persona(cls, v):
        if v not in BuilderConstants.PERSONAS.get_names():
            raise ValueError(f"Invalid persona. Must be one of {BuilderConstants.PERSONAS.get_names()}")
        return v

class LearningPathwayCreate(LearningPathwayBase):
    items: List[PathwayItemCreate]

class LearningPathwayResponse(LearningPathwayBase):
    id: int
    created_at: datetime
    updated_at: datetime
    items: List[PathwayItemResponse]
LearningContentResponse.update_forward_refs()
AssessmentQuestionResponse.update_forward_refs()