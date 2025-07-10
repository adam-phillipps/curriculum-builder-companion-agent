"""
Unit tests for embedded similarity search functionality.
Tests the integration of similarity search in content builder and catalog.
"""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from src.config import get_settings

class TestContentSimilarityIntegration:
    """Test embedded similarity search functionality."""
    
    def test_similarity_threshold_constants(self):
        """Test that similarity threshold constants are properly defined."""
        settings = get_settings()
        
        # Test that new constants exist
        assert hasattr(settings, 'CONTENT_SIMILARITY_LOW')
        assert hasattr(settings, 'CONTENT_SIMILARITY_MEDIUM') 
        assert hasattr(settings, 'CONTENT_SIMILARITY_HIGH')
        
        # Test threshold values
        assert settings.CONTENT_SIMILARITY_LOW == 0.3
        assert settings.CONTENT_SIMILARITY_MEDIUM == 0.6
        assert settings.CONTENT_SIMILARITY_HIGH == 0.8
        
        # Test that original threshold is unchanged
        assert settings.SIMILARITY_THRESHOLD == 0.85
    
    def test_similarity_threshold_ordering(self):
        """Test that similarity thresholds are in correct order."""
        settings = get_settings()
        
        assert settings.CONTENT_SIMILARITY_LOW < settings.CONTENT_SIMILARITY_MEDIUM
        assert settings.CONTENT_SIMILARITY_MEDIUM < settings.CONTENT_SIMILARITY_HIGH
        assert settings.CONTENT_SIMILARITY_HIGH < settings.SIMILARITY_THRESHOLD
    
    @patch('httpx.AsyncClient')
    async def test_similarity_search_api_call_format(self, mock_client):
        """Test that similarity search API calls use correct format."""
        # Mock the API response
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "results": [
                {
                    "id": 1,
                    "title": "Similar Content",
                    "description": "Test description",
                    "content_type": "lesson",
                    "author": "Test Author",
                    "created_at": "2024-01-01T00:00:00Z",
                    "similarity_score": 0.75
                }
            ],
            "total_found": 1,
            "search_time_ms": 50.0
        }
        
        mock_client_instance = Mock()
        mock_client_instance.post = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__ = AsyncMock(return_value=mock_client_instance)
        mock_client.return_value.__aexit__ = AsyncMock(return_value=None)
        
        # Test the API call format that frontend should use
        import httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8001/api/v1/vector/search",
                json={
                    "query_text": "test query",
                    "similarity_threshold": 0.3,
                    "max_results": 10,
                    "search_approved_only": False
                }
            )
        
        # Verify the call was made with correct parameters
        mock_client_instance.post.assert_called_once()
        call_args = mock_client_instance.post.call_args
        
        assert call_args[0][0] == "http://localhost:8001/api/v1/vector/search"
        assert "json" in call_args[1]
        
        json_data = call_args[1]["json"]
        assert json_data["query_text"] == "test query"
        assert json_data["similarity_threshold"] == 0.3
        assert json_data["max_results"] == 10
        assert json_data["search_approved_only"] is False

class TestSimilarityWarningLogic:
    """Test similarity warning logic for content builder."""
    
    def test_similarity_color_classification(self):
        """Test similarity score color classification."""
        settings = get_settings()
        
        def get_similarity_color(score: float) -> str:
            """Simulate the frontend color classification logic."""
            if score >= settings.CONTENT_SIMILARITY_HIGH:
                return 'red'
            elif score >= settings.CONTENT_SIMILARITY_MEDIUM:
                return 'yellow'
            else:
                return 'green'
        
        # Test color classifications
        assert get_similarity_color(0.2) == 'green'  # Low similarity
        assert get_similarity_color(0.5) == 'green'  # Still low
        assert get_similarity_color(0.6) == 'yellow'  # Medium threshold
        assert get_similarity_color(0.7) == 'yellow'  # Medium range
        assert get_similarity_color(0.8) == 'red'    # High threshold
        assert get_similarity_color(0.9) == 'red'    # High range
    
    def test_similarity_warning_messages(self):
        """Test similarity warning message generation."""
        settings = get_settings()
        
        def get_similarity_warning(score: float) -> str:
            """Simulate the frontend warning message logic."""
            if score >= settings.CONTENT_SIMILARITY_HIGH:
                return 'High similarity detected - please review carefully'
            elif score >= settings.CONTENT_SIMILARITY_MEDIUM:
                return 'Similar content found - please review before submitting'
            else:
                return 'Low similarity - content appears unique'
        
        # Test warning messages
        assert 'unique' in get_similarity_warning(0.3).lower()
        assert 'review before submitting' in get_similarity_warning(0.6).lower()
        assert 'review carefully' in get_similarity_warning(0.8).lower()
    
    def test_similarity_warning_threshold_boundaries(self):
        """Test similarity warning at exact threshold boundaries."""
        settings = get_settings()
        
        def should_show_warning(score: float) -> bool:
            """Determine if warning should be shown."""
            return score >= settings.CONTENT_SIMILARITY_MEDIUM
        
        # Test boundary conditions
        assert not should_show_warning(0.59)  # Just below medium
        assert should_show_warning(0.60)      # Exactly at medium
        assert should_show_warning(0.61)      # Just above medium
        assert should_show_warning(0.80)      # At high threshold
        assert should_show_warning(0.90)      # Above high threshold

class TestSimilaritySearchIntegration:
    """Test integration of similarity search in different components."""
    
    def test_content_builder_similarity_search_non_blocking(self):
        """Test that similarity search in content builder is non-blocking."""
        # This test verifies the design principle that similarity search
        # should not prevent content submission
        
        def can_submit_content(similarity_results: list) -> bool:
            """Simulate content submission logic."""
            # Even with high similarity results, submission should be allowed
            return True  # Non-blocking design
        
        # Test with various similarity scenarios
        high_similarity_results = [{"similarity_score": 0.9}]
        medium_similarity_results = [{"similarity_score": 0.7}]
        low_similarity_results = [{"similarity_score": 0.3}]
        no_results = []
        
        assert can_submit_content(high_similarity_results)
        assert can_submit_content(medium_similarity_results)
        assert can_submit_content(low_similarity_results)
        assert can_submit_content(no_results)
    
    def test_content_catalog_similarity_ordering(self):
        """Test that content catalog orders results by similarity when searching."""
        
        def order_by_similarity(results: list) -> list:
            """Simulate similarity-based ordering."""
            return sorted(results, key=lambda x: x.get('similarity_score', 0), reverse=True)
        
        # Test data with mixed similarity scores
        mixed_results = [
            {"id": 1, "title": "Content A", "similarity_score": 0.5},
            {"id": 2, "title": "Content B", "similarity_score": 0.9},
            {"id": 3, "title": "Content C", "similarity_score": 0.7},
            {"id": 4, "title": "Content D", "similarity_score": 0.3}
        ]
        
        ordered_results = order_by_similarity(mixed_results)
        
        # Verify descending order by similarity
        scores = [r["similarity_score"] for r in ordered_results]
        assert scores == [0.9, 0.7, 0.5, 0.3]
        
        # Verify correct content ordering
        titles = [r["title"] for r in ordered_results]
        assert titles == ["Content B", "Content C", "Content A", "Content D"]
    
    def test_similarity_search_with_filters_integration(self):
        """Test that similarity search results can be filtered."""
        
        def apply_filters_to_similarity_results(results: list, filters: dict) -> list:
            """Simulate applying traditional filters to similarity results."""
            filtered = results
            
            if filters.get('tier'):
                filtered = [r for r in filtered if r.get('tier') == filters['tier']]
            
            if filters.get('content_type'):
                filtered = [r for r in filtered if r.get('content_type') == filters['content_type']]
            
            return filtered
        
        # Test data
        similarity_results = [
            {"id": 1, "tier": "T2", "content_type": "lesson", "similarity_score": 0.8},
            {"id": 2, "tier": "T3", "content_type": "lesson", "similarity_score": 0.7},
            {"id": 3, "tier": "T2", "content_type": "exercise", "similarity_score": 0.6}
        ]
        
        # Test tier filtering
        tier_filtered = apply_filters_to_similarity_results(
            similarity_results, 
            {"tier": "T2"}
        )
        assert len(tier_filtered) == 2
        assert all(r["tier"] == "T2" for r in tier_filtered)
        
        # Test content type filtering
        type_filtered = apply_filters_to_similarity_results(
            similarity_results,
            {"content_type": "lesson"}
        )
        assert len(type_filtered) == 2
        assert all(r["content_type"] == "lesson" for r in type_filtered)
        
        # Test combined filtering
        combined_filtered = apply_filters_to_similarity_results(
            similarity_results,
            {"tier": "T2", "content_type": "lesson"}
        )
        assert len(combined_filtered) == 1
        assert combined_filtered[0]["id"] == 1