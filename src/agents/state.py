from typing import Dict, List, Optional, Any
from typing_extensions import TypedDict, Annotated
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

# LangGraph State (TypedDict with Annotated fields)
class AgentState(TypedDict):
    # Input data
    raw_content: Annotated[str, "Raw content to process"]
    user_id: Annotated[Optional[str], "User who submitted content"]
    model_provider: Annotated[str, "LLM provider (openai, anthropic)"]
    model_name: Annotated[str, "Specific model name"]
    
    # User suggestions
    title: Annotated[Optional[str], "User provided title"]
    suggested_tier: Annotated[Optional[str], "User suggested difficulty tier"]
    suggested_tags: Annotated[List[str], "User suggested tags"]
    suggested_personas: Annotated[List[str], "User suggested target personas"]
    suggested_content_type: Annotated[Optional[str], "User suggested content type"]
    suggested_duration: Annotated[Optional[int], "User suggested duration in minutes"]
    suggested_sandbox_type: Annotated[Optional[str], "User suggested sandbox environment"]
    author: Annotated[Optional[str], "Content author"]
    co_authors: Annotated[Optional[str], "Additional contributors"]
    sources: Annotated[Optional[str], "Reference sources and materials"]
    artifacts: Annotated[Optional[str], "Links to supplementary materials"]
    ai_assisted: Annotated[Optional[str], "AI tools used in content creation"]
    
    # Extracted metadata
    extracted_metadata: Annotated[Dict[str, Any], "AI extracted metadata"]
    
    # Similarity analysis
    similar_content: Annotated[List[Dict[str, Any]], "Similar existing content"]
    similarity_score: Annotated[Optional[float], "Highest similarity score"]
    
    # Review process
    status: Annotated[str, "Current workflow status"]
    human_review_required: Annotated[bool, "Whether human review is needed"]
    review_feedback: Annotated[Optional[str], "Human reviewer feedback"]
    
    # Final content
    content_id: Annotated[Optional[int], "Created content database ID"]
    
    # Error handling
    error_message: Annotated[Optional[str], "Error details if any"]
    retry_count: Annotated[int, "Number of retry attempts"]

# Keep Pydantic model for API validation
class WorkflowState(BaseModel):
    model_config = {"protected_namespaces": ()}
    
    # Input data
    raw_content: str
    user_id: Optional[str] = None
    model_provider: str = "openai"
    model_name: str = "gpt-4"
    
    # User suggestions
    title: Optional[str] = None
    suggested_tier: Optional[str] = None
    suggested_tags: List[str] = []
    suggested_personas: List[str] = []
    suggested_content_type: Optional[str] = None
    suggested_duration: Optional[int] = None
    suggested_sandbox_type: Optional[str] = None
    author: Optional[str] = None
    co_authors: Optional[str] = None
    sources: Optional[str] = None
    artifacts: Optional[str] = None
    ai_assisted: Optional[str] = None
    
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
    
    def to_agent_state(self) -> AgentState:
        """Convert Pydantic model to LangGraph AgentState."""
        return AgentState(
            raw_content=self.raw_content,
            user_id=self.user_id,
            model_provider=self.model_provider,
            model_name=self.model_name,
            title=self.title,
            suggested_tier=self.suggested_tier,
            suggested_tags=self.suggested_tags,
            suggested_personas=self.suggested_personas,
            suggested_content_type=self.suggested_content_type,
            suggested_duration=self.suggested_duration,
            suggested_sandbox_type=self.suggested_sandbox_type,
            author=self.author,
            co_authors=self.co_authors,
            sources=self.sources,
            artifacts=self.artifacts,
            ai_assisted=self.ai_assisted,
            extracted_metadata=self.extracted_metadata,
            similar_content=self.similar_content,
            similarity_score=self.similarity_score,
            status=self.status.value,
            human_review_required=self.human_review_required,
            review_feedback=self.review_feedback,
            content_id=self.content_id,
            error_message=self.error_message,
            retry_count=self.retry_count
        )
    
    @classmethod
    def from_agent_state(cls, agent_state: AgentState) -> "WorkflowState":
        """Convert LangGraph AgentState back to Pydantic model."""
        return cls(
            raw_content=agent_state["raw_content"],
            user_id=agent_state.get("user_id"),
            model_provider=agent_state.get("model_provider", "openai"),
            model_name=agent_state.get("model_name", "gpt-4"),
            title=agent_state.get("title"),
            suggested_tier=agent_state.get("suggested_tier"),
            suggested_tags=agent_state.get("suggested_tags", []),
            suggested_personas=agent_state.get("suggested_personas", []),
            suggested_content_type=agent_state.get("suggested_content_type"),
            suggested_duration=agent_state.get("suggested_duration"),
            suggested_sandbox_type=agent_state.get("suggested_sandbox_type"),
            author=agent_state.get("author"),
            co_authors=agent_state.get("co_authors"),
            sources=agent_state.get("sources"),
            artifacts=agent_state.get("artifacts"),
            ai_assisted=agent_state.get("ai_assisted"),
            extracted_metadata=agent_state.get("extracted_metadata", {}),
            similar_content=agent_state.get("similar_content", []),
            similarity_score=agent_state.get("similarity_score"),
            status=WorkflowStatus(agent_state.get("status", WorkflowStatus.PENDING.value)),
            human_review_required=agent_state.get("human_review_required", False),
            review_feedback=agent_state.get("review_feedback"),
            content_id=agent_state.get("content_id"),
            error_message=agent_state.get("error_message"),
            retry_count=agent_state.get("retry_count", 0)
        )