"""
Test cases for the specific user sign-out bug when loading content catalog.
These tests should FAIL with current bug, then PASS when bug is fixed.
"""
import pytest
from httpx import AsyncClient
from src.main import app

class TestUserSignOutBug:
    """Test the specific bug where users get signed out when loading content catalog."""
    
    @pytest.mark.asyncio
    async def test_user_session_persists_during_content_loading(self):
        """Test that user session is not affected by content loading operations."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Step 1: Create a user
            user_data = {
                "first_name": "Test",
                "last_name": "User",
                "current_role": "learner"
            }
            
            create_response = await client.post("/users/", json=user_data)
            assert create_response.status_code == 201, "Failed to create user"
            
            user = create_response.json()
            user_id = user["id"]
            
            # Step 2: Sign in the user
            sign_in_data = {"user_id": user_id}
            sign_in_response = await client.post("/users/sign-in", json=sign_in_data)
            assert sign_in_response.status_code == 200, "Failed to sign in"
            
            # Verify user is signed in
            initial_user_check = await client.get(f"/users/{user_id}")
            assert initial_user_check.status_code == 200, "User should be accessible after sign in"
            
            # Step 3: Load content catalog (this is where the bug might occur)
            content_response = await client.get("/api/v1/content")
            
            # Content loading should work
            assert content_response.status_code in [200, 404], f"Content loading failed: {content_response.status_code}"
            
            # Step 4: Verify user is STILL signed in (this is the critical test)
            # The bug is that this step fails - user gets signed out
            post_content_user_check = await client.get(f"/users/{user_id}")
            assert post_content_user_check.status_code == 200, "❌ BUG: User was signed out after loading content catalog!"
            
            # Verify user data is intact
            user_data_after = post_content_user_check.json()
            assert user_data_after["id"] == user_id, "User ID changed after content loading"
            assert user_data_after["current_role"] == "learner", "User role changed after content loading"
            assert user_data_after["first_name"] == "Test", "User data corrupted after content loading"
    
    @pytest.mark.asyncio
    async def test_multiple_content_requests_dont_break_session(self):
        """Test that multiple content requests don't cause session issues."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Create and sign in user
            user_data = {
                "first_name": "Persistent",
                "last_name": "Session",
                "current_role": "builder"
            }
            
            create_response = await client.post("/users/", json=user_data)
            assert create_response.status_code == 201
            
            user = create_response.json()
            user_id = user["id"]
            
            sign_in_response = await client.post("/users/sign-in", json={"user_id": user_id})
            assert sign_in_response.status_code == 200
            
            # Make multiple content requests (simulating user browsing catalog)
            for request_num in range(1, 4):
                # Load content
                content_response = await client.get("/api/v1/content")
                assert content_response.status_code in [200, 404], f"Content request {request_num} failed"
                
                # Verify user is still signed in after each request
                user_check = await client.get(f"/users/{user_id}")
                assert user_check.status_code == 200, f"❌ BUG: User signed out after content request {request_num}!"
                
                user_data_check = user_check.json()
                assert user_data_check["id"] == user_id, f"User session corrupted on request {request_num}"
                assert user_data_check["current_role"] == "builder", f"User role changed on request {request_num}"
    
    @pytest.mark.asyncio
    async def test_content_loading_with_different_user_roles_preserves_sessions(self):
        """Test that content loading preserves sessions for all user role types."""
        test_roles = ["learner", "builder", "curriculum_architect", "admin"]
        
        for role in test_roles:
            async with AsyncClient(app=app, base_url="http://test") as client:
                # Create user with specific role
                user_data = {
                    "first_name": f"Test_{role}",
                    "last_name": "User",
                    "current_role": role
                }
                
                create_response = await client.post("/users/", json=user_data)
                assert create_response.status_code == 201, f"Failed to create {role} user"
                
                user = create_response.json()
                user_id = user["id"]
                
                # Sign in user
                sign_in_response = await client.post("/users/sign-in", json={"user_id": user_id})
                assert sign_in_response.status_code == 200, f"Failed to sign in {role} user"
                
                # Load content catalog
                content_response = await client.get("/api/v1/content")
                assert content_response.status_code in [200, 404], f"Content loading failed for {role}"
                
                # Critical test: verify user with this role is still signed in
                user_check = await client.get(f"/users/{user_id}")
                assert user_check.status_code == 200, f"❌ BUG: {role} user was signed out after content loading!"
                
                user_data_check = user_check.json()
                assert user_data_check["current_role"] == role, f"❌ BUG: {role} user role was changed after content loading!"
    
    @pytest.mark.asyncio
    async def test_concurrent_user_sessions_not_affected_by_content_loading(self):
        """Test that content loading by one user doesn't affect other user sessions."""
        async with AsyncClient(app=app, base_url="http://test") as client:
            # Create two users
            user1_data = {"first_name": "User1", "current_role": "learner"}
            user2_data = {"first_name": "User2", "current_role": "builder"}
            
            user1_response = await client.post("/users/", json=user1_data)
            user2_response = await client.post("/users/", json=user2_data)
            
            assert user1_response.status_code == 201
            assert user2_response.status_code == 201
            
            user1 = user1_response.json()
            user2 = user2_response.json()
            
            # Sign in both users
            await client.post("/users/sign-in", json={"user_id": user1["id"]})
            await client.post("/users/sign-in", json={"user_id": user2["id"]})
            
            # User1 loads content
            content_response = await client.get("/api/v1/content")
            assert content_response.status_code in [200, 404]
            
            # Verify both users are still signed in
            user1_check = await client.get(f"/users/{user1['id']}")
            user2_check = await client.get(f"/users/{user2['id']}")
            
            assert user1_check.status_code == 200, "❌ BUG: User1 signed out after content loading!"
            assert user2_check.status_code == 200, "❌ BUG: User2 affected by User1's content loading!"
            
            # Verify user data integrity
            user1_data_check = user1_check.json()
            user2_data_check = user2_check.json()
            
            assert user1_data_check["current_role"] == "learner", "User1 role corrupted"
            assert user2_data_check["current_role"] == "builder", "User2 role corrupted"

if __name__ == "__main__":
    pytest.main([__file__])