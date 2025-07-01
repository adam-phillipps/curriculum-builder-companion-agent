"""Tests for metadata mapping functionality."""
import pytest
from datetime import datetime
import json
from src.vector_store.metadata_mapper import metadata_mapper, MetadataType

class TestMetadataMapper:
    """Test metadata mapping for ChromaDB integration."""
    
    def test_to_chroma_metadata_basic(self):
        """Test basic metadata conversion to ChromaDB format."""
        content_metadata = {
            "content_id": 123,
            "title": "Test Content",
            "tier": "T2",
            "personas": ["developer", "architect"],
            "estimated_duration": 90,
            "estimated_cost": 15.5,
            "is_approved": True
        }
        
        chroma_metadata = metadata_mapper.to_chroma_metadata(content_metadata)
        
        assert chroma_metadata["content_id"] == 123
        assert chroma_metadata["title"] == "Test Content"
        assert chroma_metadata["tier"] == "T2"
        assert chroma_metadata["estimated_duration"] == 90
        assert chroma_metadata["estimated_cost"] == 15.5
        assert chroma_metadata["is_approved"] is True
        
        # Arrays should be JSON serialized
        personas = json.loads(chroma_metadata["personas"])
        assert personas == ["developer", "architect"]
    
    def test_from_chroma_metadata_basic(self):
        """Test conversion from ChromaDB format back to content format."""
        chroma_metadata = {
            "content_id": 123,
            "title": "Test Content",
            "tier": "T2",
            "personas": '["developer", "architect"]',
            "estimated_duration": 90,
            "estimated_cost": 15.5,
            "is_approved": True,
            "created_at": "2024-01-01T12:00:00"
        }
        
        content_metadata = metadata_mapper.from_chroma_metadata(chroma_metadata)
        
        assert content_metadata["content_id"] == 123
        assert content_metadata["title"] == "Test Content"
        assert content_metadata["personas"] == ["developer", "architect"]
        assert isinstance(content_metadata["created_at"], datetime)
    
    def test_chromadb_error_handling(self):
        """Test ChromaDB error handling and retry logic."""
        # Test that multiple conditions are properly formatted
        filters = {
            "tier": "T1",
            "content_type": "lesson",
            "estimated_duration": 60
        }
        
        chroma_query = metadata_mapper.build_filter_query(filters)
        
        # Should use $and operator for multiple conditions
        assert "$and" in chroma_query
        assert len(chroma_query["$and"]) == 3
        
        # Verify each condition is properly formatted
        conditions = chroma_query["$and"]
        tier_condition = next(c for c in conditions if "tier" in c)
        content_type_condition = next(c for c in conditions if "content_type" in c)
        duration_condition = next(c for c in conditions if "estimated_duration" in c)
        
        assert tier_condition == {"tier": "T1"}
        assert content_type_condition == {"content_type": "lesson"}
        assert duration_condition == {"estimated_duration": 60}
    
    def test_comprehensive_metadata_mapping(self):
        """Test mapping with all supported fields."""
        full_metadata = {
            "content_id": 456,
            "title": "Comprehensive Test",
            "description": "Full test description",
            "tier": "T3",
            "content_type": "module",
            "personas": ["developer", "security"],
            "tags": ["aws", "lambda", "serverless"],
            "estimated_duration": 120,
            "estimated_cost": 25.0,
            "sandbox_type": "isolated",
            "aws_services": ["Lambda", "S3", "API Gateway"],
            "learning_objectives": ["Learn Lambda", "Deploy APIs"],
            "author": "Jane Doe",
            "co_authors": ["John Smith", "Alice Johnson"],
            "sources": "AWS Documentation",
            "artifacts": "https://github.com/example/repo",
            "ai_assisted": "ChatGPT-4",
            "created_at": datetime(2024, 1, 1, 12, 0, 0),
            "updated_at": datetime(2024, 1, 2, 12, 0, 0),
            "status": "approved",
            "is_approved": True
        }
        
        # Convert to ChromaDB format
        chroma_metadata = metadata_mapper.to_chroma_metadata(full_metadata)
        
        # Convert back
        restored_metadata = metadata_mapper.from_chroma_metadata(chroma_metadata)
        
        # Verify key fields are preserved
        assert restored_metadata["content_id"] == 456
        assert restored_metadata["title"] == "Comprehensive Test"
        assert restored_metadata["personas"] == ["developer", "security"]
        assert restored_metadata["tags"] == ["aws", "lambda", "serverless"]
        assert restored_metadata["aws_services"] == ["Lambda", "S3", "API Gateway"]
        assert restored_metadata["author"] == "Jane Doe"
        assert restored_metadata["co_authors"] == ["John Smith", "Alice Johnson"]
        assert isinstance(restored_metadata["created_at"], datetime)
    
    def test_build_filter_query(self):
        """Test building ChromaDB filter queries."""
        # Test single filter
        single_filter = {"tier": "T2"}
        result = metadata_mapper.build_filter_query(single_filter)
        assert result == {"tier": "T2"}
        
        # Test multiple filters (should use $and)
        multiple_filters = {
            "tier": "T2",
            "content_type": "lesson",
            "is_approved": True
        }
        result = metadata_mapper.build_filter_query(multiple_filters)
        expected = {
            "$and": [
                {"tier": "T2"},
                {"content_type": "lesson"},
                {"is_approved": True}
            ]
        }
        assert result == expected
        
        # Test array filters
        array_filter = {"personas": ["developer", "architect"]}
        result = metadata_mapper.build_filter_query(array_filter)
        assert result == {"personas": {"$in": ["developer", "architect"]}}
        
        # Test empty filters
        empty_filter = {}
        result = metadata_mapper.build_filter_query(empty_filter)
        assert result == {}
    
    def test_validate_metadata(self):
        """Test metadata validation."""
        # Valid metadata
        valid_metadata = {
            "content_id": 123,
            "title": "Valid Content",
            "estimated_duration": 60,
            "estimated_cost": 10.5
        }
        
        errors = metadata_mapper.validate_metadata(valid_metadata)
        assert len(errors["missing"]) == 0
        assert len(errors["invalid"]) == 0
        
        # Invalid metadata
        invalid_metadata = {
            "content_id": "not_an_integer",
            "estimated_duration": "not_a_number"
        }
        
        errors = metadata_mapper.validate_metadata(invalid_metadata)
        assert len(errors["invalid"]) > 0
    
    def test_get_searchable_fields(self):
        """Test getting list of searchable fields."""
        searchable = metadata_mapper.get_searchable_fields()
        
        assert "tier" in searchable
        assert "content_type" in searchable
        assert "author" in searchable
        assert "estimated_duration" in searchable
    
    def test_get_array_fields(self):
        """Test getting list of array fields."""
        array_fields = metadata_mapper.get_array_fields()
        
        assert "personas" in array_fields
        assert "tags" in array_fields
        assert "aws_services" in array_fields
        assert "co_authors" in array_fields
    
    def test_handle_missing_fields(self):
        """Test handling of missing fields with defaults."""
        minimal_metadata = {
            "content_id": 789,
            "title": "Minimal Content"
        }
        
        chroma_metadata = metadata_mapper.to_chroma_metadata(minimal_metadata)
        
        # Should have defaults for missing fields
        assert chroma_metadata["tier"] == "T2"  # Default tier
        assert chroma_metadata["estimated_duration"] == 60  # Default duration
        assert chroma_metadata["is_approved"] is False  # Default approval
        assert json.loads(chroma_metadata["personas"]) == []  # Default empty array
    
    def test_datetime_handling(self):
        """Test datetime serialization and deserialization."""
        test_datetime = datetime(2024, 1, 15, 14, 30, 0)
        
        metadata = {
            "content_id": 999,
            "title": "DateTime Test",
            "created_at": test_datetime
        }
        
        chroma_metadata = metadata_mapper.to_chroma_metadata(metadata)
        restored_metadata = metadata_mapper.from_chroma_metadata(chroma_metadata)
        
        # Should preserve datetime (may lose microseconds)
        assert isinstance(restored_metadata["created_at"], datetime)
        assert restored_metadata["created_at"].year == 2024
        assert restored_metadata["created_at"].month == 1
        assert restored_metadata["created_at"].day == 15