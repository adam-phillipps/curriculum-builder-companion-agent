from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from enum import Enum

class WorkflowStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SIMILARITY_CHECK = "similarity_check"
    HUMAN_REVIEW = "human_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    PUBLISHED = "published"
    ERROR = "error"

class WorkflowState(BaseModel):
    model_config = {"protected_namespaces": ()}
    
    # Input data
    raw_content: str
    user_id: Optional[str] = None
    model_provider: str = "openai"
    model_name: str = "gpt-4"
    
    # User suggestions
    suggested_tier: Optional[str] = None
    suggested_tags: List[str] = []
    suggested_personas: List[str] = []
    suggested_content_type: Optional[str] = None
    
    # Extracted metadata
    extracted_metadata: Dict[str, Any] = {}
    
    # Similarity analysis
    similar_content: List[Dict[str, Any]] = []
    similarity_score: Optional[float] = None
    
    # Review process
    status: WorkflowStatus = WorkflowStatus.PENDING
    human_review_required: bool = False
    review_feedback: Optional[str] = None
    
    # Final content
    content_id: Optional[int] = None
    
    # Error handling
    error_message: Optional[str] = None
    retry_count: int = 0