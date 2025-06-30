from typing import Dict, Any
from langgraph.graph import StateGraph, END
from sqlalchemy.ext.asyncio import AsyncSession

from .state import WorkflowState, WorkflowStatus, AgentState
from .tools import extract_metadata_from_content, create_content_tools
from src.config import get_settings

settings = get_settings()

class ContentProcessingWorkflow:
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self.content_tools = create_content_tools(db_session)
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        
        workflow = StateGraph(AgentState)
        
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
    
    async def _extract_metadata(self, state: AgentState) -> dict:
        """Extract metadata from raw content."""
        try:
            print(f"DEBUG: Extracting metadata for content: {state['raw_content'][:100]}...")
            # Call the tool with proper parameter mapping
            metadata = await extract_metadata_from_content.ainvoke({
                "content": state["raw_content"],
                "suggested_tier": state.get("suggested_tier"),
                "suggested_personas": state.get("suggested_personas", []),
                "suggested_content_type": state.get("suggested_content_type"),
                "model_provider": state.get("model_provider", "openai"),
                "model_name": state.get("model_name", "gpt-4")
            })
            
            print(f"DEBUG: Extracted metadata: {metadata}")
            
            return {
                "extracted_metadata": metadata,
                "status": WorkflowStatus.PROCESSING.value
            }
            
        except Exception as e:
            print(f"DEBUG: Metadata extraction error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": WorkflowStatus.ERROR.value,
                "error_message": str(e)
            }
    
    async def _check_similarity(self, state: AgentState) -> dict:
        """Check for similar content."""
        try:
            print(f"DEBUG: Checking similarity for metadata: {state.get('extracted_metadata', {})}")
            # Get the search tool from our factory
            search_tool = self.content_tools[0]  # search_similar_content
            similar_content = await search_tool.ainvoke({
                "metadata": state["extracted_metadata"],
                "threshold": settings.SIMILARITY_THRESHOLD
            })
            
            # Calculate max similarity score
            max_similarity = max(
                [item.get("similarity_score", 0) for item in similar_content],
                default=0
            )
            
            print(f"DEBUG: Found {len(similar_content)} similar items, max score: {max_similarity}")
            
            return {
                "similar_content": similar_content,
                "similarity_score": max_similarity,
                "status": WorkflowStatus.SIMILARITY_CHECK.value
            }
            
        except Exception as e:
            print(f"DEBUG: Similarity check error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "status": WorkflowStatus.ERROR.value,
                "error_message": str(e)
            }
    
    def _should_require_review(self, state: AgentState) -> str:
        """Determine if human review is required."""
        if state.get("status") == WorkflowStatus.ERROR.value:
            return "error"
        
        # Require review if similarity is high or human review is always required
        similarity_score = state.get("similarity_score", 0)
        if (similarity_score and similarity_score > settings.SIMILARITY_THRESHOLD) or settings.HUMAN_REVIEW_REQUIRED:
            return "review"
        
        return "publish"
    
    async def _human_review(self, state: AgentState) -> dict:
        """Handle human review process."""
        # For now, this is a placeholder that auto-approves
        # In production, this would integrate with your review API
        
        return {
            "status": WorkflowStatus.APPROVED.value,
            "human_review_required": True,
            "review_feedback": "Auto-approved for development"
        }
    
    async def _publish_content(self, state: AgentState) -> dict:
        """Publish content to database."""
        try:
            # Get the create tool from our factory
            create_tool = self.content_tools[1]  # create_learning_content
            content_id = await create_tool.ainvoke({
                "metadata": state["extracted_metadata"],
                "raw_content": state["raw_content"],
                "user_id": state.get("user_id")
            })
            
            return {
                "content_id": content_id,
                "status": WorkflowStatus.PUBLISHED.value
            }
            
        except Exception as e:
            return {
                "status": WorkflowStatus.ERROR.value,
                "error_message": str(e)
            }
    
    async def _handle_error(self, state: AgentState) -> dict:
        """Handle workflow errors."""
        return {
            "status": WorkflowStatus.ERROR.value,
            "error_message": state.get("error_message", "Unknown error occurred")
        }
    
    async def process_content(self, initial_state: WorkflowState) -> WorkflowState:
        """Process content through the workflow."""
        # Convert Pydantic model to AgentState for LangGraph
        agent_state = initial_state.to_agent_state()
        result = await self.graph.ainvoke(agent_state)
        
        # Convert result back to Pydantic model
        return WorkflowState.from_agent_state(result)