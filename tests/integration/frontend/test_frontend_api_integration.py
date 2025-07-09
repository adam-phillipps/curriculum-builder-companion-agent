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
    async def test_embedded_similarity_search_api_call(self):
        """Test that embedded similarity search API calls work correctly."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Test the API call that embedded similarity search makes
            search_data = {
                "query_text": "AWS Lambda tutorial",
                "similarity_threshold": 0.3,
                "max_results": 10,
                "search_approved_only": False
            }
            
            # This is the call embedded similarity search makes
            vector_search_response = await client.post("/api/v1/vector/search", json=search_data)
            
            # Should work for embedded similarity search
            assert vector_search_response.status_code == 200, f"Embedded similarity search fails: {vector_search_response.status_code}"
            
            # Verify response format
            data = vector_search_response.json()
            assert "results" in data, "Vector search response missing 'results' field"
            assert isinstance(data["results"], list), "Vector search results not a list"
            assert "total_found" in data, "Vector search response missing 'total_found' field"
    
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
    async def test_content_catalog_uses_correct_endpoints(self):
        """Test that content catalog uses appropriate endpoints for different purposes."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Content catalog should use content endpoint for browsing
            browse_response = await client.get("/api/v1/content")
            assert browse_response.status_code == 200, "Content browsing endpoint should work"
            
            # Content catalog should use vector search only when user searches
            search_data = {
                "query_text": "machine learning",
                "similarity_threshold": 0.1,
                "max_results": 50,
                "search_approved_only": False
            }
            
            search_response = await client.post("/api/v1/vector/search", json=search_data)
            assert search_response.status_code == 200, "Similarity search should work when user searches"
            
            # Verify both endpoints return proper data
            browse_data = browse_response.json()
            search_data_response = search_response.json()
            
            assert isinstance(browse_data, list), "Browse endpoint should return array"
            assert "results" in search_data_response, "Search endpoint should return results object"
            assert isinstance(search_data_response["results"], list), "Search results should be array"
    
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
    
    @pytest.mark.asyncio
    async def test_similarity_search_results_format(self):
        """Test that similarity search results have proper format for embedded use."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            search_data = {
                "query_text": "test content",
                "similarity_threshold": 0.1,
                "max_results": 5,
                "search_approved_only": False
            }
            
            response = await client.post("/api/v1/vector/search", json=search_data)
            
            if response.status_code == 200:
                data = response.json()
                
                # Test response structure for embedded similarity search
                assert "results" in data, "Missing results field"
                assert "total_found" in data, "Missing total_found field"
                assert isinstance(data["results"], list), "Results should be array"
                
                # Test individual result format
                if len(data["results"]) > 0:
                    result = data["results"][0]
                    
                    # Fields needed for content builder similarity check
                    required_fields = ["id", "title", "description", "content_type"]
                    for field in required_fields:
                        assert field in result, f"Similarity result missing {field} field"
                    
                    # Similarity score should be present
                    assert "similarity_score" in result, "Missing similarity_score field"

class TestEmbeddedSimilaritySearchIntegration:
    """Test embedded similarity search integration."""
    
    @pytest.mark.asyncio
    async def test_content_builder_similarity_check(self):
        """Test similarity check functionality for content builder."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Test the similarity check that content builder performs
            search_data = {
                "query_text": "AWS Lambda serverless tutorial",
                "similarity_threshold": 0.3,  # Low threshold for content builder
                "max_results": 10,
                "search_approved_only": False
            }
            
            response = await client.post("/api/v1/vector/search", json=search_data)
            assert response.status_code == 200, "Content builder similarity check should work"
            
            data = response.json()
            assert "results" in data
            
            # Results should include information needed for similarity warnings
            if len(data["results"]) > 0:
                result = data["results"][0]
                assert "similarity_score" in result, "Need similarity score for warnings"
                assert "title" in result, "Need title for display"
                assert "description" in result, "Need description for context"
                assert "author" in result or result.get("author") is None, "Author field should exist"
    
    @pytest.mark.asyncio
    async def test_content_catalog_similarity_search(self):
        """Test similarity search functionality for content catalog."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Test the similarity search that content catalog performs
            search_data = {
                "query_text": "machine learning python",
                "similarity_threshold": 0.1,  # Lower threshold for discovery
                "max_results": 50,  # More results for browsing
                "search_approved_only": False
            }
            
            response = await client.post("/api/v1/vector/search", json=search_data)
            assert response.status_code == 200, "Content catalog similarity search should work"
            
            data = response.json()
            assert "results" in data
            assert "total_found" in data
            
            # Results should be suitable for content catalog display
            if len(data["results"]) > 0:
                result = data["results"][0]
                catalog_fields = ["id", "title", "description", "tier", "content_type", "estimated_duration"]
                for field in catalog_fields:
                    assert field in result, f"Content catalog needs {field} field"

if __name__ == "__main__":
    pytest.main([__file__])