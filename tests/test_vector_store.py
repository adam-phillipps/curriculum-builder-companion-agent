"""Tests for vector store functionality."""
import pytest
from unittest.mock import Mock, patch
from src.services.vector_store import VectorStoreService

class TestVectorStoreService:
    """Test vector store service functionality."""
    
    @patch('src.services.vector_store.chromadb.HttpClient')
    def test_vector_store_initialization(self, mock_client):
        """Test vector store service initialization."""
        mock_collection = Mock()
        mock_client.return_value.get_collection.side_effect = Exception("Not found")
        mock_client.return_value.create_collection.return_value = mock_collection
        
        service = VectorStoreService()
        
        assert service.client is not None
        assert service.approved_collection is not None
        assert service.draft_collection is not None
    
    def test_generate_content_id(self):
        """Test content ID generation."""
        with patch('src.services.vector_store.chromadb.HttpClient'):
            service = VectorStoreService()
            
            content_id = 123
            content_hash = "abcdef1234567890"
            
            result = service._generate_content_id(content_id, content_hash)
            
            assert result == "content_123_abcdef12"
    
    def test_hash_content(self):
        """Test content hashing."""
        with patch('src.services.vector_store.chromadb.HttpClient'):
            service = VectorStoreService()
            
            content = "Test content for hashing"
            hash1 = service._hash_content(content)
            hash2 = service._hash_content(content)
            
            assert hash1 == hash2  # Same content should produce same hash
            assert len(hash1) == 64  # SHA256 produces 64 character hex string
    
    @patch('src.services.vector_store.chromadb.HttpClient')
    def test_add_content(self, mock_client):
        """Test adding content to vector store."""
        mock_collection = Mock()
        mock_client.return_value.get_collection.side_effect = Exception("Not found")
        mock_client.return_value.create_collection.return_value = mock_collection
        
        service = VectorStoreService()
        
        metadata = {
            "tier": "T2",
            "content_type": "lesson",
            "personas": ["developer"],
            "aws_services": ["Lambda"],
            "estimated_duration": 60,
            "estimated_cost": 5.0,
            "sandbox_type": "individual"
        }
        
        vector_id = service.add_content(
            content_id=1,
            title="Test Content",
            description="Test description",
            content_text="This is test content",
            metadata=metadata,
            is_approved=False
        )
        
        assert vector_id.startswith("content_1_")
        mock_collection.add.assert_called_once()
    
    @patch('src.services.vector_store.chromadb.HttpClient')
    def test_find_similar_content(self, mock_client):
        """Test finding similar content."""
        mock_collection = Mock()
        mock_client.return_value.get_collection.side_effect = Exception("Not found")
        mock_client.return_value.create_collection.return_value = mock_collection
        
        # Mock ChromaDB query response
        mock_collection.query.return_value = {
            "documents": [["Test document content"]],
            "metadatas": [[{
                "content_id": 1,
                "title": "Similar Content",
                "description": "Similar description",
                "tier": "T2",
                "content_type": "lesson",
                "personas": '["developer"]',
                "aws_services": '["Lambda"]',
                "estimated_duration": 60,
                "estimated_cost": 5.0
            }]],
            "distances": [[0.2]]  # 0.2 distance = 0.8 similarity
        }
        
        service = VectorStoreService()
        
        results = service.find_similar_content(
            query_text="Test query",
            similarity_threshold=0.7,
            max_results=5
        )
        
        assert len(results) == 1
        assert results[0]["content_id"] == 1
        assert results[0]["similarity_score"] == 0.8
        assert results[0]["title"] == "Similar Content"
    
    @patch('src.services.vector_store.chromadb.HttpClient')
    def test_get_content_stats(self, mock_client):
        """Test getting content statistics."""
        mock_approved = Mock()
        mock_draft = Mock()
        mock_approved.count.return_value = 10
        mock_draft.count.return_value = 5
        
        mock_client.return_value.get_collection.side_effect = Exception("Not found")
        mock_client.return_value.create_collection.side_effect = [mock_approved, mock_draft]
        
        service = VectorStoreService()
        
        stats = service.get_content_stats()
        
        assert stats["approved_content_count"] == 10
        assert stats["draft_content_count"] == 5
        assert stats["total_content_count"] == 15
    
    @patch('src.services.vector_store.chromadb.HttpClient')
    def test_find_similar_content_with_filters(self, mock_client):
        """Test finding similar content with metadata filters."""
        mock_collection = Mock()
        mock_client.return_value.get_collection.side_effect = Exception("Not found")
        mock_client.return_value.create_collection.return_value = mock_collection
        
        mock_collection.query.return_value = {
            "documents": [[]],
            "metadatas": [[]],
            "distances": [[]]
        }
        
        service = VectorStoreService()
        
        metadata_filters = {
            "tier": "T2",
            "content_type": "lesson",
            "estimated_duration": 60
        }
        
        service.find_similar_content(
            query_text="Test query",
            metadata_filters=metadata_filters,
            similarity_threshold=0.8
        )
        
        # Verify query was called with where clause
        mock_collection.query.assert_called_once()
        call_args = mock_collection.query.call_args
        assert "where" in call_args.kwargs
        where_clause = call_args.kwargs["where"]
        assert where_clause["tier"] == "T2"
        assert where_clause["content_type"] == "lesson"
    
    @patch('src.services.vector_store.chromadb.HttpClient')
    def test_find_similar_content_error_handling(self, mock_client):
        """Test error handling in similarity search."""
        mock_collection = Mock()
        mock_client.return_value.get_collection.side_effect = Exception("Not found")
        mock_client.return_value.create_collection.return_value = mock_collection
        
        # Make query raise an exception
        mock_collection.query.side_effect = Exception("ChromaDB error")
        
        service = VectorStoreService()
        
        results = service.find_similar_content(
            query_text="Test query",
            similarity_threshold=0.8
        )
        
        # Should return empty list on error
        assert results == []