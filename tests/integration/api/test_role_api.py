"""
Test cases for role-related API endpoints.
"""
import pytest
from httpx import AsyncClient
from src.main import app

class TestRoleAPI:
    """Test role-related API endpoints."""
    
    @pytest.mark.asyncio
    async def test_get_available_roles_endpoint(self):
        """Test that available roles endpoint returns correct profile roles."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/users/roles/available")
            
            assert response.status_code == 200
            roles = response.json()
            
            expected_roles = ["learner", "builder", "curriculum_architect", "admin"]
            assert roles == expected_roles
            assert len(roles) == 4
    
    @pytest.mark.asyncio
    async def test_get_available_career_roles_endpoint(self):
        """Test that career roles endpoint returns job/career roles."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get("/users/career-roles/available")
            
            assert response.status_code == 200
            career_roles = response.json()
            
            expected_careers = ["developer", "architect", "operations", "security", "data_engineer", "ml_engineer", "all_roles"]
            assert career_roles == expected_careers
            assert len(career_roles) == 7
    
    @pytest.mark.asyncio
    async def test_create_user_with_valid_profile_role(self):
        """Test creating user with valid profile role."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            user_data = {
                "first_name": "Test",
                "last_name": "User",
                "current_role": "learner",
                "career_role": "developer"
            }
            
            response = await client.post("/users/", json=user_data)
            
            assert response.status_code == 201
            user = response.json()
            assert user["current_role"] == "learner"
            assert user["career_role"] == "developer"
    
    @pytest.mark.asyncio
    async def test_create_user_with_invalid_profile_role(self):
        """Test creating user with invalid profile role fails."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            user_data = {
                "first_name": "Test",
                "last_name": "User", 
                "current_role": "invalid_role"
            }
            
            response = await client.post("/users/", json=user_data)
            
            assert response.status_code == 400
            error = response.json()
            assert "Invalid profile role" in error["detail"]
    
    @pytest.mark.asyncio
    async def test_role_separation_in_responses(self):
        """Test that API responses properly separate profile and career roles."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Create user with both roles
            user_data = {
                "first_name": "Test",
                "last_name": "User",
                "current_role": "builder",
                "career_role": "ml_engineer"
            }
            
            create_response = await client.post("/users/", json=user_data)
            assert create_response.status_code == 201
            
            user = create_response.json()
            user_id = user["id"]
            
            # Get user and verify role separation
            get_response = await client.get(f"/users/{user_id}")
            assert get_response.status_code == 200
            
            retrieved_user = get_response.json()
            assert retrieved_user["current_role"] == "builder"  # Profile role
            assert retrieved_user["career_role"] == "ml_engineer"  # Career role

if __name__ == "__main__":
    pytest.main([__file__])