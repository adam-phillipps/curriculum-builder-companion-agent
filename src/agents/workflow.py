from typing import Dict, Any
from langgraph.graph import StateGraph, END
from sqlalchemy.ext.asyncio import AsyncSession

from .state import WorkflowState, WorkflowStatus
from .tools import extract_metadata_from_content, search_similar_content, create_learning_content
from src.config import get_settings

settings = get_settings()

class ContentProcessingWorkflow:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("extract_metadata", self._extract_metadata)
        workflow.add_node("check_similarity", self._check_similarity)
        workflow.add_node("human_review", self._human_review)
        workflow.add_node("publish_content", self._publish_content)
        workflow.add_node("handle_error", self._handle_error)
        
        # Define edges
        workflow.set_entry_point("extract_metadata")
        
        workflow.add_edge("extract_metadata", "check_similarity")
        
        # Conditional edge based on similarity score
        workflow.add_conditional_edges(
            "check_similarity",
            self._should_require_review,
            {
                "review": "human_review",
                "publish": "publish_content",
                "error": "handle_error"
            }
        )
        
        workflow.add_edge("human_review", "publish_content")
        workflow.add_edge("publish_content", END)
        workflow.add_edge("handle_error", END)
        
        return workflow.compile()
    
    async def _extract_metadata(self, state: WorkflowState) -> Dict[str, Any]:
        """Extract metadata from raw content."""
        try:
            state.status = WorkflowStatus.PROCESSING
            
            metadata = await extract_metadata_from_content(
                content=state.raw_content,
                suggested_tier=state.suggested_tier,
                suggested_personas=state.suggested_personas,
                suggested_content_type=state.suggested_content_type,
                model_provider=state.model_provider,
                model_name=state.model_name
            )
            
            state.extracted_metadata = metadata
            return {"extracted_metadata": metadata, "status": WorkflowStatus.PROCESSING}
            
        except Exception as e:
            return {
                "status": WorkflowStatus.ERROR,
                "error_message": str(e)
            }
    
    async def _check_similarity(self, state: WorkflowState) -> Dict[str, Any]:
        """Check for similar content."""
        try:
            state.status = WorkflowStatus.SIMILARITY_CHECK
            
            similar_content = await search_similar_content(
                metadata=state.extracted_metadata,
                db_session=self.db_session,
                threshold=settings.SIMILARITY_THRESHOLD
            )
            
            # Calculate max similarity score
            max_similarity = max(
                [item.get("similarity_score", 0) for item in similar_content],
                default=0
            )
            
            return {
                "similar_content": similar_content,
                "similarity_score": max_similarity,
                "status": WorkflowStatus.SIMILARITY_CHECK
            }
            
        except Exception as e:
            return {
                "status": WorkflowStatus.ERROR,
                "error_message": str(e)
            }
    
    def _should_require_review(self, state: WorkflowState) -> str:
        """Determine if human review is required."""
        if state.status == WorkflowStatus.ERROR:
            return "error"
        
        # Require review if similarity is high or human review is always required
        if (state.similarity_score and state.similarity_score > settings.SIMILARITY_THRESHOLD) or settings.HUMAN_REVIEW_REQUIRED:
            return "review"
        
        return "publish"
    
    async def _human_review(self, state: WorkflowState) -> Dict[str, Any]:
        """Handle human review process."""
        # For now, this is a placeholder that auto-approves
        # In production, this would integrate with your review API
        
        return {
            "status": WorkflowStatus.APPROVED,
            "human_review_required": True,
            "review_feedback": "Auto-approved for development"
        }
    
    async def _publish_content(self, state: WorkflowState) -> Dict[str, Any]:
        """Publish content to database."""
        try:
            content_id = await create_learning_content(
                metadata=state.extracted_metadata,
                raw_content=state.raw_content,
                db_session=self.db_session,
                user_id=state.user_id
            )
            
            return {
                "content_id": content_id,
                "status": WorkflowStatus.PUBLISHED
            }
            
        except Exception as e:
            return {
                "status": WorkflowStatus.ERROR,
                "error_message": str(e)
            }
    
    async def _handle_error(self, state: WorkflowState) -> Dict[str, Any]:
        """Handle workflow errors."""
        return {
            "status": WorkflowStatus.ERROR,
            "error_message": state.error_message or "Unknown error occurred"
        }
    
    async def process_content(self, initial_state: WorkflowState) -> WorkflowState:
        """Process content through the workflow."""
        result = await self.graph.ainvoke(initial_state.model_dump())
        return WorkflowState(**result)