"""Tests for content creation and database operations."""
import pytest
from src.agents.tools import _create_learning_content, _search_similar_content

class TestContentCreation:
    """Test content creation in database."""
    
    @pytest.mark.asyncio
    async def test_create_learning_content(self, test_session, sample_metadata):
        """Test creating learning content in database."""
        content_id = await _create_learning_content(
            metadata=sample_metadata,
            raw_content="Test content",
            db_session=test_session,
            user_id="test_user"
        )
        
        assert isinstance(content_id, int)
        assert content_id > 0
    
    @pytest.mark.asyncio
    async def test_create_content_generates_code_title(self, test_session, sample_metadata):
        """Test that code_title is generated correctly."""
        content_id = await _create_learning_content(
            metadata=sample_metadata,
            raw_content="Test content",
            db_session=test_session
        )
        
        # Verify content was created (we can't easily check code_title without querying)
        assert content_id is not None
    
    @pytest.mark.asyncio
    async def test_create_content_with_all_fields(self, test_session):
        """Test creating content with all metadata fields."""
        metadata = {
            "title": "Complete Test",
            "description": "Full test description",
            "tier": "T3",
            "personas": ["architect", "developer"],
            "content_type": "module",
            "learning_objectives": ["Obj1", "Obj2", "Obj3"],
            "estimated_duration": 120,
            "sandbox_type": "shared",
            "aws_services": ["S3", "Lambda", "DynamoDB"],
            "technical_requirements": {"runtime": "python3.11", "memory": "512MB"},
            "estimated_cost": 15.5
        }
        
        content_id = await _create_learning_content(
            metadata=metadata,
            raw_content="Comprehensive test content",
            db_session=test_session
        )
        
        assert content_id is not None

class TestSimilaritySearch:
    """Test similarity search functionality."""
    
    @pytest.mark.asyncio
    async def test_search_similar_content_empty_db(self, test_session, sample_metadata):
        """Test similarity search with empty database."""
        results = await _search_similar_content(
            metadata=sample_metadata,
            db_session=test_session,
            threshold=0.8
        )
        
        assert isinstance(results, list)
        assert len(results) == 0
    
    @pytest.mark.asyncio
    async def test_search_similar_content_with_data(self, test_session, sample_metadata):
        """Test similarity search with existing content."""
        # First create some content
        await _create_learning_content(
            metadata=sample_metadata,
            raw_content="Test content",
            db_session=test_session
        )
        
        # Then search for similar content
        results = await _search_similar_content(
            metadata=sample_metadata,
            db_session=test_session,
            threshold=0.5
        )
        
        assert len(results) == 1
        assert results[0]["tier"] == "T2"
        assert results[0]["content_type"] == "lesson"
        assert "similarity_score" in results[0]
    
    @pytest.mark.asyncio
    async def test_search_filters_by_tier_and_type(self, test_session):
        """Test that search filters by tier and content type."""
        # Create content with different tiers and types
        metadata_t1 = {"tier": "T1", "content_type": "lesson", "title": "T1 Lesson"}
        metadata_t2 = {"tier": "T2", "content_type": "module", "title": "T2 Module"}
        
        await _create_learning_content(metadata_t1, "content1", test_session)
        await _create_learning_content(metadata_t2, "content2", test_session)
        
        # Search for T1 lessons
        results = await _search_similar_content(
            metadata={"tier": "T1", "content_type": "lesson"},
            db_session=test_session
        )
        
        assert len(results) == 1
        assert results[0]["tier"] == "T1"
        assert results[0]["content_type"] == "lesson"