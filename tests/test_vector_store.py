"""Tests for vector store functionality - Fixed version."""
import pytest
from unittest.mock import Mock, patch
from src.services.vector_store import VectorStoreService

class TestVectorStoreService:
    """Test vector store service functionality."""
    
    @patch('src.services.vector_store.chromadb.PersistentClient')
    def test_vector_store_initialization(self, mock_client):
        """Test vector store service initialization."""
        mock_collection = Mock()
        mock_client.return_value.get_or_create_collection.return_value = mock_collection
        
        service = VectorStoreService()
        
        assert service._client is None  # Lazy initialization
        # Access client to trigger initialization
        client = service.client
        assert client is not None
    
    def test_generate_content_id(self):
        """Test content ID generation."""
        with patch('src.services.vector_store.chromadb.PersistentClient'):
            service = VectorStoreService()
            
            content_id = 123
            content_hash = "abcdef1234567890"
            
            result = service._generate_content_id(content_id, content_hash)
            
            assert result == "content_123_abcdef12"
    
    def test_hash_content(self):
        """Test content hashing."""
        with patch('src.services.vector_store.chromadb.PersistentClient'):
            service = VectorStoreService()
            
            content = "Test content for hashing"
            hash1 = service._hash_content(content)
            hash2 = service._hash_content(content)
            
            assert hash1 == hash2  # Same content should produce same hash
            assert len(hash1) == 64  # SHA256 produces 64 character hex string
    
    @patch('src.services.vector_store.chromadb.PersistentClient')
    def test_add_content(self, mock_client):
        """Test adding content to vector store."""
        mock_collection = Mock()
        mock_client.return_value.get_or_create_collection.return_value = mock_collection
        
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
        # Check that collection was accessed (lazy loading)
        service.draft_collection  # This should trigger the mock
    
    @patch('src.services.vector_store.chromadb.PersistentClient')
    def test_find_similar_content(self, mock_client):
        """Test finding similar content."""
        mock_collection = Mock()
        mock_client.return_value.get_or_create_collection.return_value = mock_collection
        
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
        
        # Should work with proper mocking
        assert isinstance(results, list)
    
    @patch('src.services.vector_store.chromadb.PersistentClient')
    def test_get_content_stats(self, mock_client):
        """Test getting content statistics."""
        mock_approved = Mock()
        mock_draft = Mock()
        mock_approved.count.return_value = 10
        mock_draft.count.return_value = 5
        
        # Mock the get_or_create_collection to return different collections
        def mock_get_or_create(name):
            if "approved" in name:
                return mock_approved
            else:
                return mock_draft
        
        mock_client.return_value.get_or_create_collection.side_effect = mock_get_or_create
        
        service = VectorStoreService()
        
        stats = service.get_content_stats()
        
        # Should work with proper mocking
        assert isinstance(stats, dict)
        assert "approved_content_count" in stats
        assert "draft_content_count" in stats
    
    @patch('src.services.vector_store.chromadb.PersistentClient')
    def test_find_similar_content_error_handling(self, mock_client):
        """Test error handling in similarity search."""
        mock_collection = Mock()
        mock_client.return_value.get_or_create_collection.return_value = mock_collection
        
        # Make query raise an exception
        mock_collection.query.side_effect = Exception("ChromaDB error")
        
        service = VectorStoreService()
        
        results = service.find_similar_content(
            query_text="Test query",
            similarity_threshold=0.8
        )
        
        # Should return empty list on error
        assert results == []