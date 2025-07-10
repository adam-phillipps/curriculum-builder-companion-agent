"""
Unit tests for vector store learning outcomes functionality.
"""
import pytest
from unittest.mock import MagicMock, patch

from src.services.vector_store import VectorStoreService


@pytest.fixture
def vector_store():
    """Create vector store instance with mocked dependencies."""
    with patch('src.services.vector_store.chromadb'):
        service = VectorStoreService()
        service._client = MagicMock()
        service._outcomes_collection = MagicMock()
        return service


@pytest.fixture
def sample_outcome_data():
    """Sample learning outcome data."""
    return {
        "outcome_id": 1,
        "name": "Python Programming",
        "description": "Learn Python fundamentals",
        "domain": "programming",
        "difficulty_level": "beginner",
        "tags": ["python", "programming", "coding"]
    }


class TestAddLearningOutcome:
    """Test adding learning outcomes to vector store."""
    
    def test_add_learning_outcome_success(self, vector_store, sample_outcome_data):
        """Test successful learning outcome addition."""
        # Setup
        vector_store.outcomes_collection.add = MagicMock()
        
        # Execute
        result = vector_store.add_learning_outcome(**sample_outcome_data)
        
        # Assert
        expected_vector_id = f"outcome_{sample_outcome_data['outcome_id']}"
        assert result == expected_vector_id
        vector_store.outcomes_collection.add.assert_called_once()
        
        # Check call arguments
        call_args = vector_store.outcomes_collection.add.call_args
        assert call_args[1]['ids'] == [expected_vector_id]
        assert len(call_args[1]['documents']) == 1
        assert len(call_args[1]['metadatas']) == 1
    
    def test_add_learning_outcome_with_existing_id(self, vector_store, sample_outcome_data):
        """Test adding learning outcome when ID already exists."""
        # Setup
        vector_store.outcomes_collection.add.side_effect = Exception("already exists")
        vector_store.outcomes_collection.update = MagicMock()
        
        # Execute
        result = vector_store.add_learning_outcome(**sample_outcome_data)
        
        # Assert
        expected_vector_id = f"outcome_{sample_outcome_data['outcome_id']}"
        assert result == expected_vector_id
        vector_store.outcomes_collection.update.assert_called_once()
    
    def test_add_learning_outcome_metadata_format(self, vector_store, sample_outcome_data):
        """Test metadata format for ChromaDB compatibility."""
        # Setup
        vector_store.outcomes_collection.add = MagicMock()
        
        # Execute
        vector_store.add_learning_outcome(**sample_outcome_data)
        
        # Assert
        call_args = vector_store.outcomes_collection.add.call_args
        metadata = call_args[1]['metadatas'][0]
        
        # Check that tags are converted to comma-separated string
        assert 'tags_str' in metadata
        assert metadata['tags_str'] == "python,programming,coding"
        assert 'tags' not in metadata  # Original list should not be in metadata


class TestFindSimilarOutcomes:
    """Test finding similar learning outcomes."""
    
    def test_find_similar_outcomes_success(self, vector_store):
        """Test successful similarity search."""
        # Setup
        mock_results = {
            "documents": [["doc1", "doc2"]],
            "metadatas": [[
                {
                    "outcome_id": 1,
                    "name": "Python Programming",
                    "description": "Learn Python",
                    "domain": "programming",
                    "difficulty_level": "beginner",
                    "tags_str": "python,programming"
                },
                {
                    "outcome_id": 2,
                    "name": "Java Programming",
                    "description": "Learn Java",
                    "domain": "programming", 
                    "difficulty_level": "intermediate",
                    "tags_str": "java,programming"
                }
            ]],
            "distances": [[0.2, 0.4]]
        }
        vector_store.outcomes_collection.query.return_value = mock_results
        
        # Execute
        results = vector_store.find_similar_outcomes("python programming", max_results=5)
        
        # Assert
        assert len(results) == 2
        assert results[0]["outcome_id"] == 1
        assert results[0]["name"] == "Python Programming"
        assert results[0]["tags"] == ["python", "programming"]  # Converted back to list
        assert results[0]["similarity_score"] > results[1]["similarity_score"]  # Sorted by similarity
    
    def test_find_similar_outcomes_with_domain_filter(self, vector_store):
        """Test similarity search with domain filter."""
        # Setup
        vector_store.outcomes_collection.query = MagicMock(return_value={
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]]
        })
        
        # Execute
        vector_store.find_similar_outcomes(
            "programming", 
            max_results=10, 
            domain_filter="programming"
        )
        
        # Assert
        call_args = vector_store.outcomes_collection.query.call_args
        assert call_args[1]['where'] == {"domain": "programming"}
    
    def test_find_similar_outcomes_empty_results(self, vector_store):
        """Test similarity search with no results."""
        # Setup
        vector_store.outcomes_collection.query.return_value = {
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]]
        }
        
        # Execute
        results = vector_store.find_similar_outcomes("nonexistent query")
        
        # Assert
        assert results == []
    
    def test_find_similar_outcomes_error_handling(self, vector_store):
        """Test similarity search error handling."""
        # Setup
        vector_store.outcomes_collection.query.side_effect = Exception("Search error")
        
        # Execute
        results = vector_store.find_similar_outcomes("python programming")
        
        # Assert
        assert results == []


class TestVectorStoreStats:
    """Test vector store statistics."""
    
    def test_get_content_stats_with_outcomes(self, vector_store):
        """Test getting statistics including learning outcomes."""
        # Setup - mock the underlying collection objects
        mock_approved = MagicMock()
        mock_approved.count.return_value = 50
        vector_store._approved_collection = mock_approved
        
        mock_draft = MagicMock()
        mock_draft.count.return_value = 10
        vector_store._draft_collection = mock_draft
        
        mock_outcomes = MagicMock()
        mock_outcomes.count.return_value = 25
        vector_store._outcomes_collection = mock_outcomes
        
        # Execute
        stats = vector_store.get_content_stats()
        
        # Assert
        assert stats["approved_content_count"] == 50
        assert stats["draft_content_count"] == 10
        assert stats["learning_outcomes_count"] == 25
        assert stats["total_content_count"] == 60
    
    def test_get_content_stats_error_handling(self, vector_store):
        """Test statistics error handling."""
        # Setup
        vector_store.approved_collection.count.side_effect = Exception("Count error")
        
        # Execute
        stats = vector_store.get_content_stats()
        
        # Assert
        assert "error" in stats


class TestOutcomesCollection:
    """Test outcomes collection management."""
    
    def test_outcomes_collection_lazy_initialization(self):
        """Test that outcomes collection is created lazily."""
        with patch('src.services.vector_store.chromadb'):
            service = VectorStoreService()
            mock_client = MagicMock()
            service._client = mock_client
            
            # First access should create collection
            mock_client.get_collection.side_effect = Exception("Collection not found")
            mock_client.create_collection.return_value = MagicMock()
            
            collection = service.outcomes_collection
            
            mock_client.create_collection.assert_called_once_with(
                name="learning_outcomes",
                metadata={"description": "Learning content collection: learning_outcomes"}
            )