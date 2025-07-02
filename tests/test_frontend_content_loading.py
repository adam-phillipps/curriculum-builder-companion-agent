"""
Test cases for frontend content loading issues.
These tests should FAIL with current frontend bugs, then PASS when bugs are fixed.
"""
import pytest
from httpx import AsyncClient
from src.main import app

class TestFrontendContentCatalogBugs:
    """Test frontend-specific content catalog loading issues."""
    
    @pytest.mark.asyncio
    async def test_content_api_returns_data_for_frontend(self):
        """Test that content API returns data in format expected by frontend."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/content")
            
            # This test will fail if the API doesn't return proper data structure
            # that the frontend ContentManagement component expects
            if response.status_code == 200:
                data = response.json()
                assert isinstance(data, list), "Frontend expects array of content items"
                
                # Frontend ContentManagement expects specific field structure
                if len(data) > 0:
                    first_item = data[0]
                    
                    # These are the fields the frontend ContentTile component uses
                    frontend_required_fields = [
                        "id",           # Used as key and for content identification
                        "title",        # Displayed as content title
                        "description",  # Displayed as content description
                        "tier",         # Used for tier badge
                        "content_type", # Used for content type icon
                        "estimated_duration", # Displayed as duration
                    ]
                    
                    for field in frontend_required_fields:
                        assert field in first_item, f"Frontend requires field '{field}' but it's missing from API response"
                        assert first_item[field] is not None, f"Frontend field '{field}' is null"
            else:
                # If no content, API should still return 200 with empty array, not 404
                # This is what the frontend expects for "no content found" state
                assert response.status_code == 200, f"Frontend expects 200 with empty array, got {response.status_code}"
    
    @pytest.mark.asyncio 
    async def test_content_api_handles_empty_database(self):
        """Test that content API handles empty database gracefully for frontend."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/content")
            
            # Even with empty database, frontend expects 200 status with empty array
            # Not 404 or 500 errors that would break the frontend
            assert response.status_code == 200, f"Expected 200 for empty content, got {response.status_code}"
            
            data = response.json()
            assert isinstance(data, list), "Frontend expects array even when empty"
            # Empty array is fine - frontend handles this case
    
    @pytest.mark.asyncio
    async def test_content_api_response_structure_matches_frontend_expectations(self):
        """Test that API response structure matches what frontend components expect."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/content")
            
            if response.status_code == 200:
                data = response.json()
                
                # Frontend expects direct array, not wrapped in results object
                assert isinstance(data, list), "Frontend expects direct array, not {results: [...]} wrapper"
                
                # Test that response doesn't have unexpected wrapper structure
                assert not isinstance(data, dict) or "results" not in data, "Frontend doesn't expect {results: [...]} wrapper"
                
                if len(data) > 0:
                    item = data[0]
                    
                    # Frontend ContentTile component expects these exact field names
                    expected_structure = {
                        "id": (int, "Content ID for React keys"),
                        "title": (str, "Content title for display"),
                        "description": (str, "Content description for display"),
                        "tier": (str, "Tier for badge display"),
                        "content_type": (str, "Type for icon selection"),
                        "estimated_duration": (int, "Duration for display")
                    }
                    
                    for field_name, (expected_type, description) in expected_structure.items():
                        assert field_name in item, f"Missing field '{field_name}' ({description})"
                        if item[field_name] is not None:
                            assert isinstance(item[field_name], expected_type), f"Field '{field_name}' should be {expected_type.__name__}, got {type(item[field_name])}"

class TestContentLoadingPerformance:
    """Test content loading performance issues that might cause timeouts."""
    
    @pytest.mark.asyncio
    async def test_content_api_responds_quickly(self):
        """Test that content API responds within reasonable time to prevent frontend timeouts."""
        import time
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            start_time = time.time()
            response = await client.get("/api/v1/content")
            end_time = time.time()
            
            response_time = end_time - start_time
            
            # Frontend will timeout if API takes too long
            # This test will fail if there are performance issues
            assert response_time < 10.0, f"API response too slow: {response_time:.2f}s (frontend may timeout)"
            
            # Ideally should be much faster
            if response_time > 5.0:
                pytest.fail(f"API response slow: {response_time:.2f}s (may cause poor UX)")

if __name__ == "__main__":
    pytest.main([__file__])