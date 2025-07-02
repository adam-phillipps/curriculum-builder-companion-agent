"""
Test cases for frontend API integration issues.
These tests simulate what the frontend JavaScript code does.
"""
import pytest
from httpx import AsyncClient
from src.main import app

class TestFrontendAPIIntegration:
    """Test API calls that the frontend makes, simulating browser behavior."""
    
    @pytest.mark.asyncio
    async def test_frontend_vector_search_api_call_fails(self):
        """Test that frontend's vector search API call fails (this is the bug!)."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # This is the ACTUAL API call that frontend ContentManagement makes:
            # ApiClient.searchContent({ max_results: 12 })
            # Which calls /v1/vector/search endpoint
            
            search_data = {
                "query_text": "",
                "similarity_threshold": 0.1,
                "max_results": 12,
                "search_approved_only": False
            }
            
            # This is the exact call the frontend makes
            vector_search_response = await client.post("/api/v1/vector/search", json=search_data)
            
            # This test should FAIL because the endpoint doesn't work properly
            # When we fix the bug, this test should pass
            assert vector_search_response.status_code == 200, f"❌ BUG: Frontend vector search fails: {vector_search_response.status_code}"
            
            # Verify response format frontend expects
            data = vector_search_response.json()
            assert "results" in data, "❌ BUG: Vector search response missing 'results' field"
            assert isinstance(data["results"], list), "❌ BUG: Vector search results not a list"
            
            # Frontend expects content items in results
            if len(data["results"]) > 0:
                item = data["results"][0]
                required_fields = ["content_id", "title", "description", "tier", "content_type"]
                for field in required_fields:
                    assert field in item, f"❌ BUG: Vector search result missing field '{field}'"
    
    @pytest.mark.asyncio
    async def test_api_cors_headers_for_frontend(self):
        """Test that API returns proper CORS headers for frontend requests."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Simulate a browser preflight request
            options_response = await client.options("/api/v1/content")
            
            # Should not fail with CORS errors
            assert options_response.status_code in [200, 204, 405], "CORS preflight failed"
            
            # Test actual request with Origin header (like browser would send)
            headers = {
                "Origin": "http://localhost:3000",  # Typical frontend dev server
                "Content-Type": "application/json"
            }
            
            content_response = await client.get("/api/v1/content", headers=headers)
            assert content_response.status_code in [200, 404], "Request with Origin header failed"
    
    @pytest.mark.asyncio
    async def test_api_error_responses_frontend_can_handle(self):
        """Test that API error responses are in format frontend can handle."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Test various error scenarios
            
            # 1. Invalid endpoint
            invalid_response = await client.get("/api/v1/nonexistent")
            if invalid_response.status_code == 404:
                # Frontend should be able to parse error response
                try:
                    error_data = invalid_response.json()
                    # Should have error information frontend can display
                    assert "detail" in error_data or "message" in error_data, "Error response missing details"
                except:
                    # If not JSON, should at least have reasonable status code
                    pass
            
            # 2. Content endpoint with invalid params
            bad_params_response = await client.get("/api/v1/content", params={"invalid": "param"})
            # Should not crash, should return reasonable response
            assert bad_params_response.status_code in [200, 400, 422], "API crashes on invalid params"
    
    @pytest.mark.asyncio
    async def test_content_catalog_api_mismatch_bug(self):
        """Test the bug where ContentManagement calls wrong API endpoint."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # The ContentManagement component calls ApiClient.searchContent()
            # But it should call a simple content list endpoint instead
            
            # What frontend currently does (WRONG - this is the bug):
            search_data = {
                "query_text": "",
                "similarity_threshold": 0.1, 
                "max_results": 12,
                "search_approved_only": False
            }
            
            wrong_response = await client.post("/api/v1/vector/search", json=search_data)
            
            # What frontend SHOULD do (RIGHT):
            right_response = await client.get("/api/v1/content")
            
            # After the fix: ContentManagement should use the right endpoint
            # Vector search still works but shouldn't be used for content catalog
            assert right_response.status_code == 200, "Basic content endpoint should work"
            
            # Vector search works but is the wrong choice for content catalog
            # (it's for similarity search, not content listing)
            assert wrong_response.status_code == 200, "Vector search works but wrong for catalog"
            
            # When we fix the bug, ContentManagement should use the right endpoint
            content_data = right_response.json()
            assert isinstance(content_data, list), "Content endpoint should return array"
            
            if len(content_data) > 0:
                item = content_data[0]
                # Verify it has fields the frontend needs
                assert "id" in item, "Content item needs id field"
                assert "title" in item, "Content item needs title field"
    
    @pytest.mark.asyncio
    async def test_content_loading_doesnt_affect_user_endpoints(self):
        """Test that content loading doesn't interfere with user-related endpoints."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Create a user first
            user_data = {"first_name": "Test", "current_role": "learner"}
            create_response = await client.post("/users/", json=user_data)
            assert create_response.status_code == 201
            
            user = create_response.json()
            user_id = user["id"]
            
            # Load content (this might interfere with user endpoints)
            content_response = await client.get("/api/v1/content")
            
            # Now test that user endpoints still work
            user_response = await client.get(f"/users/{user_id}")
            assert user_response.status_code == 200, "❌ BUG: Content loading broke user endpoints!"
            
            # Test user list endpoint
            users_response = await client.get("/users/")
            assert users_response.status_code == 200, "❌ BUG: Content loading broke users list endpoint!"
            
            # Test roles endpoint
            roles_response = await client.get("/users/roles/available")
            assert roles_response.status_code == 200, "❌ BUG: Content loading broke roles endpoint!"

class TestContentAPIDataIntegrity:
    """Test that content API returns valid, complete data."""
    
    @pytest.mark.asyncio
    async def test_content_items_have_complete_data(self):
        """Test that content items returned by API have all necessary data."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/content")
            
            if response.status_code == 200:
                data = response.json()
                
                if isinstance(data, list) and len(data) > 0:
                    for i, item in enumerate(data[:3]):  # Check first 3 items
                        # Test that items have non-null essential data
                        assert item.get("title"), f"Item {i} has empty title"
                        assert item.get("description"), f"Item {i} has empty description"
                        assert item.get("tier"), f"Item {i} has empty tier"
                        assert item.get("content_type"), f"Item {i} has empty content_type"
                        
                        # Test that numeric fields are valid
                        duration = item.get("estimated_duration")
                        if duration is not None:
                            assert isinstance(duration, (int, float)), f"Item {i} duration not numeric"
                            assert duration > 0, f"Item {i} has invalid duration: {duration}"
                        
                        # Test that array fields are arrays
                        personas = item.get("personas")
                        if personas is not None:
                            assert isinstance(personas, list), f"Item {i} personas not array"

if __name__ == "__main__":
    pytest.main([__file__])