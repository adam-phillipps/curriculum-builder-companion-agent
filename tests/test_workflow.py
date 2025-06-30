"""Tests for agent workflow functionality."""
import pytest
from unittest.mock import AsyncMock, patch
from src.agents.workflow import ContentProcessingWorkflow, WorkflowStatus

class TestWorkflowIntegration:
    """Test complete workflow integration."""
    
    @pytest.mark.asyncio
    async def test_workflow_initialization(self, test_session):
        """Test workflow initialization."""
        workflow = ContentProcessingWorkflow(test_session)
        
        assert workflow.db_session == test_session
        assert len(workflow.content_tools) == 2  # search and create tools
    
    @pytest.mark.asyncio
    async def test_extract_metadata_step(self, test_session):
        """Test metadata extraction step."""
        workflow = ContentProcessingWorkflow(test_session)
        
        state = {
            "raw_content": "Learn AWS Lambda with Python",
            "suggested_tier": "T2",
            "suggested_personas": ["developer"],
            "suggested_content_type": "lesson"
        }
        
        result = await workflow._extract_metadata(state)
        
        assert result["status"] == WorkflowStatus.PROCESSING.value
        assert "extracted_metadata" in result
        assert result["extracted_metadata"]["tier"] == "T2"
        assert "Lambda" in result["extracted_metadata"]["aws_services"]
    
    @pytest.mark.asyncio
    async def test_similarity_check_step(self, test_session):
        """Test similarity check step."""
        workflow = ContentProcessingWorkflow(test_session)
        
        state = {
            "extracted_metadata": {
                "tier": "T2",
                "content_type": "lesson",
                "title": "Test Content"
            }
        }
        
        result = await workflow._check_similarity(state)
        
        assert result["status"] == WorkflowStatus.SIMILARITY_CHECK.value
        assert "similar_content" in result
        assert "similarity_score" in result
        assert isinstance(result["similar_content"], list)
    
    @pytest.mark.asyncio
    async def test_human_review_decision(self, test_session):
        """Test human review decision logic."""
        workflow = ContentProcessingWorkflow(test_session)
        
        # Test high similarity requires review
        high_similarity_state = {"similarity_score": 0.9}
        result = await workflow._decide_human_review(high_similarity_state)
        assert result["human_review_required"] is True
        
        # Test low similarity doesn't require review
        low_similarity_state = {"similarity_score": 0.3}
        result = await workflow._decide_human_review(low_similarity_state)
        assert result["human_review_required"] is False
    
    @pytest.mark.asyncio
    async def test_content_creation_step(self, test_session):
        """Test content creation step."""
        workflow = ContentProcessingWorkflow(test_session)
        
        state = {
            "extracted_metadata": {
                "title": "Test Content",
                "description": "Test description",
                "tier": "T2",
                "personas": ["developer"],
                "content_type": "lesson",
                "learning_objectives": ["Learn basics"],
                "estimated_duration": 60,
                "sandbox_type": "individual",
                "aws_services": ["Lambda"],
                "technical_requirements": {"runtime": "python3.9"},
                "estimated_cost": 5.0
            },
            "raw_content": "Test content",
            "human_review_required": False
        }
        
        result = await workflow._create_content(state)
        
        assert result["status"] == WorkflowStatus.PUBLISHED.value
        assert "content_id" in result
        assert isinstance(result["content_id"], int)
    
    @pytest.mark.asyncio
    async def test_workflow_error_handling(self, test_session):
        """Test workflow error handling."""
        workflow = ContentProcessingWorkflow(test_session)
        
        # Test with invalid state
        invalid_state = {"invalid": "data"}
        
        result = await workflow._extract_metadata(invalid_state)
        
        assert result["status"] == WorkflowStatus.ERROR.value
        assert "error_message" in result

class TestWorkflowStates:
    """Test workflow state management."""
    
    def test_workflow_status_enum(self):
        """Test workflow status enumeration."""
        assert WorkflowStatus.PROCESSING.value == "processing"
        assert WorkflowStatus.SIMILARITY_CHECK.value == "similarity_check"
        assert WorkflowStatus.HUMAN_REVIEW.value == "human_review"
        assert WorkflowStatus.PUBLISHED.value == "published"
        assert WorkflowStatus.ERROR.value == "error"
    
    @pytest.mark.asyncio
    async def test_state_transitions(self, test_session):
        """Test proper state transitions through workflow."""
        workflow = ContentProcessingWorkflow(test_session)
        
        initial_state = {
            "raw_content": "AWS Lambda tutorial",
            "suggested_tier": "T2",
            "suggested_personas": ["developer"],
            "suggested_content_type": "lesson"
        }
        
        # Step 1: Extract metadata
        state = await workflow._extract_metadata(initial_state)
        assert state["status"] == WorkflowStatus.PROCESSING.value
        
        # Step 2: Check similarity
        state.update(await workflow._check_similarity(state))
        assert state["status"] == WorkflowStatus.SIMILARITY_CHECK.value
        
        # Step 3: Decide human review
        state.update(await workflow._decide_human_review(state))
        
        # Step 4: Create content (if no human review needed)
        if not state.get("human_review_required", True):
            state.update(await workflow._create_content(state))
            assert state["status"] == WorkflowStatus.PUBLISHED.value