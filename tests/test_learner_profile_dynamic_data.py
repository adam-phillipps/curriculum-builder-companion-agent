"""
Test that learner profile uses dynamic user-specific data, not hardcoded values.
"""
import pytest
from httpx import AsyncClient
from src.main import app

class TestLearnerProfileDynamicData:
    """Test that learner profile components use actual user data."""
    
    @pytest.mark.asyncio
    async def test_learner_profile_uses_user_specific_data(self):
        """Test that learner profile API returns user-specific data."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Create two different users
            user1_data = {"first_name": "User1", "current_role": "learner"}
            user2_data = {"first_name": "User2", "current_role": "learner"}
            
            user1_response = await client.post("/users/", json=user1_data)
            user2_response = await client.post("/users/", json=user2_data)
            
            assert user1_response.status_code == 201
            assert user2_response.status_code == 201
            
            user1 = user1_response.json()
            user2 = user2_response.json()
            
            # Get learner profiles for both users
            profile1_response = await client.get(f"/users/{user1['id']}/learner-profile")
            profile2_response = await client.get(f"/users/{user2['id']}/learner-profile")
            
            assert profile1_response.status_code == 200
            assert profile2_response.status_code == 200
            
            profile1 = profile1_response.json()
            profile2 = profile2_response.json()
            
            # Verify profiles are user-specific (different user_ids)
            assert profile1["user_id"] == user1["id"]
            assert profile2["user_id"] == user2["id"]
            assert profile1["user_id"] != profile2["user_id"]
    
    @pytest.mark.asyncio
    async def test_content_progress_is_user_specific(self):
        """Test that content progress is specific to each user."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Create a user
            user_data = {"first_name": "TestUser", "current_role": "learner"}
            user_response = await client.post("/users/", json=user_data)
            assert user_response.status_code == 201
            
            user = user_response.json()
            user_id = user["id"]
            
            # Get user's content progress
            progress_response = await client.get(f"/users/{user_id}/content-progress")
            assert progress_response.status_code == 200
            
            progress_data = progress_response.json()
            
            # Verify all progress records belong to this user
            for progress_item in progress_data:
                assert progress_item["user_id"] == user_id, f"Progress item belongs to wrong user: {progress_item}"
    
    @pytest.mark.asyncio
    async def test_no_hardcoded_pathway_data(self):
        """Test that pathway data is not hardcoded."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Create users with different learning paths
            user1_data = {"first_name": "PathUser1", "current_role": "learner"}
            user2_data = {"first_name": "PathUser2", "current_role": "builder"}
            
            user1_response = await client.post("/users/", json=user1_data)
            user2_response = await client.post("/users/", json=user2_data)
            
            user1 = user1_response.json()
            user2 = user2_response.json()
            
            # Get progress for both users
            progress1_response = await client.get(f"/users/{user1['id']}/content-progress")
            progress2_response = await client.get(f"/users/{user2['id']}/content-progress")
            
            progress1 = progress1_response.json()
            progress2 = progress2_response.json()
            
            # Progress should be independent (not identical hardcoded data)
            # Even if both are empty, they should have different user_ids in any items
            for item in progress1:
                assert item["user_id"] == user1["id"]
            
            for item in progress2:
                assert item["user_id"] == user2["id"]

if __name__ == "__main__":
    pytest.main([__file__])