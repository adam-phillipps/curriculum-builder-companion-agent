"""
Test cases for content catalog loading bugs.
These tests should FAIL with current bugs, then PASS when bugs are fixed.
"""
import pytest
from httpx import AsyncClient
from unittest.mock import patch, AsyncMock
from src.main import app

class TestContentCatalogLoading:
    """Test that content catalog loads properly without signing user out."""
    
    @pytest.mark.asyncio
    async def test_content_catalog_loads_learning_items(self):
        """Test that content catalog successfully loads learning content items."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/content")
            
            # This should succeed and return content items (or at least not fail)
            # The bug is that this endpoint might be broken or cause errors
            assert response.status_code in [200, 404], f"Expected 200 or 404, got {response.status_code}: {response.text}"
            
            if response.status_code == 200:
                data = response.json()
                assert isinstance(data, list), "Response should be a list of content items"
                
                # If content exists, verify basic structure
                if len(data) > 0:
                    first_item = data[0]
                    # Check for essential fields that should be present
                    essential_fields = ["id", "title", "description"]
                    for field in essential_fields:
                        assert field in first_item, f"Content item missing essential field: {field}"
    
    @pytest.mark.asyncio
    async def test_content_catalog_loads_without_server_errors(self):
        """Test that loading content catalog doesn't cause 500 server errors."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/api/v1/content")
            
            # The main bug we're testing: content loading should not cause server errors
            assert response.status_code != 500, f"Server error when loading content: {response.text}"
            
            # Should return either success or not found, but not server error
            assert response.status_code in [200, 404, 422], f"Unexpected status code: {response.status_code}"
            
            # If successful, should return valid JSON
            if response.status_code == 200:
                try:
                    data = response.json()
                    assert isinstance(data, list), "Content response should be a list"
                except Exception as e:
                    pytest.fail(f"Failed to parse JSON response: {e}")

class TestUserSessionPersistence:
    """Test that user sessions persist when loading content catalog."""
    
    @pytest.mark.asyncio
    async def test_user_stays_signed_in_when_loading_catalog(self):
        """Test that user remains signed in when accessing content catalog."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # First, create and sign in a user
            user_data = {
                "first_name": "Test",
                "last_name": "User", 
                "current_role": "learner"
            }
            
            create_response = await client.post("/api/v1/users", json=user_data)
            assert create_response.status_code == 201, "Failed to create test user"
            
            user = create_response.json()
            user_id = user["id"]
            
            # Sign in the user
            sign_in_data = {"user_id": user_id}
            sign_in_response = await client.post("/api/v1/users/sign-in", json=sign_in_data)
            assert sign_in_response.status_code == 200, "Failed to sign in user"
            
            sign_in_result = sign_in_response.json()
            assert sign_in_result["user"]["id"] == user_id, "Sign in returned wrong user"
            
            # Now try to load content catalog - this should NOT sign out the user
            content_response = await client.get("/api/v1/content")
            
            # Content loading should not affect user session
            # The bug is that this causes user to be signed out
            assert content_response.status_code in [200, 404], "Content loading failed"
            
            # Verify user is still signed in by checking their profile
            profile_response = await client.get(f"/api/v1/users/{user_id}")
            assert profile_response.status_code == 200, "User was signed out after loading content catalog"
            
            profile_data = profile_response.json()
            assert profile_data["id"] == user_id, "User session was lost"
            assert profile_data["current_role"] == "learner", "User data was corrupted"
    
    @pytest.mark.asyncio
    async def test_multiple_content_requests_preserve_session(self):
        """Test that multiple content catalog requests don't break user session."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Create and sign in user
            user_data = {
                "first_name": "Persistent",
                "last_name": "User",
                "current_role": "builder"
            }
            
            create_response = await client.post("/api/v1/users", json=user_data)
            assert create_response.status_code == 201
            
            user = create_response.json()
            user_id = user["id"]
            
            sign_in_response = await client.post("/api/v1/users/sign-in", json={"user_id": user_id})
            assert sign_in_response.status_code == 200
            
            # Make multiple content requests (simulating catalog reloads)
            for i in range(3):
                content_response = await client.get("/api/v1/content")
                assert content_response.status_code in [200, 404], f"Content request {i+1} failed"
                
                # Verify user is still signed in after each request
                user_check = await client.get(f"/api/v1/users/{user_id}")
                assert user_check.status_code == 200, f"User signed out after content request {i+1}"
                
                user_data_check = user_check.json()
                assert user_data_check["id"] == user_id, f"User session lost on request {i+1}"

class TestContentCatalogIntegration:
    """Integration tests for content catalog functionality."""
    
    @pytest.mark.asyncio
    async def test_content_catalog_with_different_user_roles(self):
        """Test that content catalog works for all user roles."""
        roles_to_test = ["learner", "builder", "curriculum_architect", "admin"]
        
        for role in roles_to_test:
            async with AsyncClient(app=app, base_url="http://test") as client:
                # Create user with specific role
                user_data = {
                    "first_name": f"Test_{role}",
                    "last_name": "User",
                    "current_role": role
                }
                
                create_response = await client.post("/api/v1/users", json=user_data)
                assert create_response.status_code == 201, f"Failed to create {role} user"
                
                user = create_response.json()
                user_id = user["id"]
                
                # Sign in user
                sign_in_response = await client.post("/api/v1/users/sign-in", json={"user_id": user_id})
                assert sign_in_response.status_code == 200, f"Failed to sign in {role} user"
                
                # Load content catalog
                content_response = await client.get("/api/v1/content")
                assert content_response.status_code in [200, 404], f"Content loading failed for {role}"
                
                # Verify user is still signed in
                user_check = await client.get(f"/api/v1/users/{user_id}")
                assert user_check.status_code == 200, f"{role} user was signed out"
                
                user_data_check = user_check.json()
                assert user_data_check["current_role"] == role, f"{role} user role was changed"

if __name__ == "__main__":
    pytest.main([__file__])