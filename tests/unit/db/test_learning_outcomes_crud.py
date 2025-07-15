"""
Unit tests for learning outcomes CRUD operations.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.crud.learning_outcomes import (
    create_learning_outcome, get_learning_outcome, get_learning_outcomes,
    update_learning_outcome_status, search_similar_outcomes
)
from src.db.models.learning_outcomes import LearningOutcome


@pytest.fixture
def mock_db():
    """Mock database session."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def sample_outcome_data():
    """Sample learning outcome data."""
    return {
        "name": "Python Programming",
        "description": "Learn Python fundamentals",
        "domain": "programming",
        "difficulty_level": "beginner",
        "tags": ["python", "programming"],
        "status": "approved"
    }


class TestCreateLearningOutcome:
    """Test learning outcome creation."""
    
    @pytest.mark.asyncio
    @patch('src.db.crud.learning_outcomes.vector_store')
    async def test_create_learning_outcome_success(self, mock_vector_store, mock_db, sample_outcome_data):
        """Test successful learning outcome creation."""
        # Setup
        mock_outcome = LearningOutcome(id=1, **sample_outcome_data)
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        mock_db.refresh.side_effect = lambda obj: setattr(obj, 'id', 1)
        mock_vector_store.add_learning_outcome = MagicMock()
        
        # Execute
        result = await create_learning_outcome(
            db=mock_db,
            **sample_outcome_data
        )
        
        # Assert
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
        mock_vector_store.add_learning_outcome.assert_called_once()
        assert result.name == sample_outcome_data["name"]
        assert result.domain == sample_outcome_data["domain"]
    
    @pytest.mark.asyncio
    @patch('src.db.crud.learning_outcomes.vector_store')
    async def test_create_learning_outcome_vector_store_failure(self, mock_vector_store, mock_db, sample_outcome_data):
        """Test learning outcome creation when vector store fails."""
        # Setup
        mock_outcome = LearningOutcome(id=1, **sample_outcome_data)
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        mock_db.refresh.side_effect = lambda obj: setattr(obj, 'id', 1)
        mock_vector_store.add_learning_outcome.side_effect = Exception("Vector store error")
        
        # Execute - should not raise exception
        result = await create_learning_outcome(
            db=mock_db,
            **sample_outcome_data
        )
        
        # Assert - outcome still created despite vector store failure
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        assert result.name == sample_outcome_data["name"]


class TestGetLearningOutcome:
    """Test learning outcome retrieval."""
    
    @pytest.mark.asyncio
    async def test_get_learning_outcome_found(self, mock_db, sample_outcome_data):
        """Test successful learning outcome retrieval."""
        # Setup
        mock_outcome = LearningOutcome(id=1, **sample_outcome_data)
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_outcome
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        # Execute
        result = await get_learning_outcome(mock_db, 1)
        
        # Assert
        assert result == mock_outcome
        mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_learning_outcome_not_found(self, mock_db):
        """Test learning outcome retrieval when not found."""
        # Setup
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        # Execute
        result = await get_learning_outcome(mock_db, 999)
        
        # Assert
        assert result is None


class TestGetLearningOutcomes:
    """Test learning outcomes listing with filters."""
    
    @pytest.mark.asyncio
    async def test_get_learning_outcomes_no_filters(self, mock_db, sample_outcome_data):
        """Test listing all learning outcomes."""
        # Setup
        mock_outcomes = [LearningOutcome(id=i, **sample_outcome_data) for i in range(1, 4)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_outcomes
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        # Execute
        result = await get_learning_outcomes(mock_db)
        
        # Assert
        assert len(result) == 3
        mock_db.execute.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_learning_outcomes_with_filters(self, mock_db, sample_outcome_data):
        """Test listing learning outcomes with filters."""
        # Setup
        mock_outcomes = [LearningOutcome(id=1, **sample_outcome_data)]
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_outcomes
        mock_db.execute = AsyncMock(return_value=mock_result)
        
        # Execute
        result = await get_learning_outcomes(
            mock_db, 
            status="approved", 
            domain="programming",
            skip=0,
            limit=10
        )
        
        # Assert
        assert len(result) == 1
        mock_db.execute.assert_called_once()


class TestUpdateLearningOutcomeStatus:
    """Test learning outcome status updates."""
    
    @pytest.mark.asyncio
    @patch('src.db.crud.learning_outcomes.get_learning_outcome')
    async def test_update_status_success(self, mock_get, mock_db, sample_outcome_data):
        """Test successful status update."""
        # Setup
        mock_outcome = LearningOutcome(id=1, **sample_outcome_data)
        mock_get.return_value = mock_outcome
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        
        # Execute
        result = await update_learning_outcome_status(mock_db, 1, "rejected")
        
        # Assert
        assert result.status == "rejected"
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once()
    
    @pytest.mark.asyncio
    @patch('src.db.crud.learning_outcomes.get_learning_outcome')
    async def test_update_status_not_found(self, mock_get, mock_db):
        """Test status update when outcome not found."""
        # Setup
        mock_get.return_value = None
        
        # Execute
        result = await update_learning_outcome_status(mock_db, 999, "approved")
        
        # Assert
        assert result is None


class TestSearchSimilarOutcomes:
    """Test vector similarity search."""
    
    @pytest.mark.asyncio
    @patch('src.db.crud.learning_outcomes.vector_store')
    async def test_search_similar_outcomes_success(self, mock_vector_store):
        """Test successful similarity search."""
        # Setup
        mock_results = [
            {
                "outcome_id": 1,
                "name": "Python Programming",
                "description": "Learn Python",
                "domain": "programming",
                "difficulty_level": "beginner",
                "tags": ["python"],
                "similarity_score": 0.85
            }
        ]
        mock_vector_store.find_similar_outcomes.return_value = mock_results
        
        # Execute
        result = await search_similar_outcomes("python programming")
        
        # Assert
        assert len(result) == 1
        assert result[0]["similarity_score"] == 0.85
        mock_vector_store.find_similar_outcomes.assert_called_once_with(
            query_text="python programming",
            max_results=10,
            domain_filter=None
        )
    
    @pytest.mark.asyncio
    @patch('src.db.crud.learning_outcomes.vector_store')
    async def test_search_similar_outcomes_error(self, mock_vector_store):
        """Test similarity search with error."""
        # Setup
        mock_vector_store.find_similar_outcomes.side_effect = Exception("Search error")
        
        # Execute
        result = await search_similar_outcomes("python programming")
        
        # Assert
        assert result == []


class TestLearningOutcomeBugFixes:
    """Test fixes for learning outcome bugs discovered in production."""
    
    @pytest.mark.asyncio
    @patch('src.db.crud.learning_outcomes.vector_store')
    async def test_create_outcome_handles_vector_store_permission_error(self, mock_vector_store, mock_db, sample_outcome_data):
        """Test that outcome creation continues when vector store has permission errors."""
        # Setup - simulate cache permission error
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        mock_db.refresh.side_effect = lambda obj: setattr(obj, 'id', 1)
        mock_vector_store.add_learning_outcome.side_effect = PermissionError("Permission denied: '/home/appuser/.cache'")
        
        # Execute - should not raise exception
        result = await create_learning_outcome(
            db=mock_db,
            **sample_outcome_data
        )
        
        # Assert - outcome still created despite vector store cache error
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        assert result.name == sample_outcome_data["name"]
    
    @pytest.mark.asyncio
    @patch('src.db.crud.learning_outcomes.vector_store')
    async def test_create_outcome_handles_chromadb_connection_error(self, mock_vector_store, mock_db, sample_outcome_data):
        """Test that outcome creation continues when ChromaDB is unreachable."""
        # Setup - simulate ChromaDB connection error
        mock_db.add = MagicMock()
        mock_db.commit = AsyncMock()
        mock_db.refresh = AsyncMock()
        mock_db.refresh.side_effect = lambda obj: setattr(obj, 'id', 1)
        mock_vector_store.add_learning_outcome.side_effect = ConnectionError("Could not connect to ChromaDB")
        
        # Execute - should not raise exception
        result = await create_learning_outcome(
            db=mock_db,
            **sample_outcome_data
        )
        
        # Assert - outcome still created despite ChromaDB connection error
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        assert result.name == sample_outcome_data["name"]
    
    @pytest.mark.asyncio
    @patch('src.db.crud.learning_outcomes.vector_store')
    async def test_search_similar_outcomes_handles_cache_permission_error(self, mock_vector_store):
        """Test that similarity search handles cache permission errors gracefully."""
        # Setup - simulate cache permission error
        mock_vector_store.find_similar_outcomes.side_effect = PermissionError("[Errno 13] Permission denied: '/home/appuser/.cache'")
        
        # Execute - should not raise exception
        result = await search_similar_outcomes("python programming")
        
        # Assert - returns empty list instead of crashing
        assert result == []
        mock_vector_store.find_similar_outcomes.assert_called_once()