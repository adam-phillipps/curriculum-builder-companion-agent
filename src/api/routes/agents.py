from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db
from src.agents.workflow import ContentProcessingWorkflow
from src.agents.state import WorkflowState, WorkflowStatus

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])

class ContentSubmissionRequest(BaseModel):
    model_config = {"protected_namespaces": ()}
    
    content: str
    user_id: Optional[str] = None
    model_provider: str = "openai"
    model_name: str = "gpt-4"
    suggested_tier: Optional[str] = None
    suggested_tags: List[str] = []
    suggested_personas: List[str] = []
    suggested_content_type: Optional[str] = None

class ContentSubmissionResponse(BaseModel):
    workflow_id: str
    status: str  # Changed from WorkflowStatus to str for JSON serialization
    content_id: Optional[int] = None
    extracted_metadata: dict = {}
    similar_content: List[dict] = []
    similarity_score: Optional[float] = None
    human_review_required: bool = False
    error_message: Optional[str] = None

@router.post("/process-content", response_model=ContentSubmissionResponse)
async def process_content(
    request: ContentSubmissionRequest,
    db: AsyncSession = Depends(get_db)
):
    """Process learning content through the agent workflow."""
    
    try:
        # Create initial workflow state
        initial_state = WorkflowState(
            raw_content=request.content,
            user_id=request.user_id,
            model_provider=request.model_provider,
            model_name=request.model_name,
            suggested_tier=request.suggested_tier,
            suggested_tags=request.suggested_tags,
            suggested_personas=request.suggested_personas,
            suggested_content_type=request.suggested_content_type
        )
        
        # Process through workflow
        workflow = ContentProcessingWorkflow(db)
        final_state = await workflow.process_content(initial_state)
        
        # Generate workflow ID (in production, store this in Redis/DB)
        import uuid
        workflow_id = str(uuid.uuid4())
        
        return ContentSubmissionResponse(
            workflow_id=workflow_id,
            status=final_state.status.value,  # Convert enum to string
            content_id=final_state.content_id,
            extracted_metadata=final_state.extracted_metadata,
            similar_content=final_state.similar_content,
            similarity_score=final_state.similarity_score,
            human_review_required=final_state.human_review_required,
            error_message=final_state.error_message
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/workflow/{workflow_id}")
async def get_workflow_status(workflow_id: str):
    """Get workflow status (placeholder for future implementation)."""
    # In production, retrieve from Redis/DB
    return {"workflow_id": workflow_id, "status": "completed"}

@router.post("/review/{workflow_id}")
async def submit_human_review(
    workflow_id: str,
    approved: bool,
    feedback: Optional[str] = None
):
    """Submit human review decision (placeholder for future implementation)."""
    # In production, update workflow state and continue processing
    return {
        "workflow_id": workflow_id,
        "approved": approved,
        "feedback": feedback,
        "status": "review_submitted"
    }