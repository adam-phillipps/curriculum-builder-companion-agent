"""
Tests for user API endpoints.
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.main import app
from src.db.crud.user import create_user
from src.api.schemas.user import UserCreate
from src.api.dependencies import get_db

@pytest.mark.asyncio
async def test_create_user_endpoint(db_session: AsyncSession):
    """Test creating a user via API."""
    import uuid
    unique_email = f"api.john.doe.{uuid.uuid4().hex[:8]}@example.com"
    
    # Override the database dependency to use test session
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    try:
        async with AsyncClient(app=app, base_url="http://test") as client:
            user_data = {
                "first_name": "John",
                "last_name": "Doe",
                "email": unique_email,
                "current_role": "learner"
            }
            
            response = await client.post("/users/", json=user_data)
            
            assert response.status_code == 201
            data = response.json()
            assert data["first_name"] == "John"
            assert data["last_name"] == "Doe"
            assert data["email"] == unique_email
            assert data["current_role"] == "learner"
            assert data["is_active"] is True
    finally:
        # Clean up dependency override
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_create_user_invalid_role():
    """Test creating a user with invalid role."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        user_data = {
            "first_name": "John",
            "current_role": "invalid_role"
        }
        
        response = await client.post("/users/", json=user_data)
        
        assert response.status_code == 400
        assert "Invalid profile role" in response.json()["detail"]

@pytest.mark.asyncio
async def test_get_users_endpoint():
    """Test getting list of users via API."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/users/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

@pytest.mark.asyncio
async def test_get_user_by_id_endpoint(db_session: AsyncSession):
    """Test getting a user by ID via API."""
    # Override the database dependency to use test session
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    try:
        # Create a user first
        user_data = UserCreate(
            first_name="Test",
            last_name="User",
            current_role="learner"
        )
        user = await create_user(db_session, user_data)
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(f"/users/{user.id}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == user.id
            assert data["first_name"] == "Test"
    finally:
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_get_user_not_found():
    """Test getting a non-existent user."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/users/99999")
        
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]

@pytest.mark.asyncio
async def test_update_user_endpoint(db_session: AsyncSession):
    """Test updating a user via API."""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    try:
        # Create a user first
        user_data = UserCreate(
            first_name="Original",
            current_role="learner"
        )
        user = await create_user(db_session, user_data)
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            update_data = {
                "first_name": "Updated",
                "last_name": "Name",
                "current_role": "builder"
            }
            
            response = await client.put(f"/users/{user.id}", json=update_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["first_name"] == "Updated"
            assert data["last_name"] == "Name"
            assert data["current_role"] == "builder"
    finally:
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_sign_in_user_endpoint(db_session: AsyncSession):
    """Test user sign-in via API."""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    try:
        # Create a learner user first
        user_data = UserCreate(
            first_name="Learner",
            current_role="learner"
        )
        user = await create_user(db_session, user_data)
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            sign_in_data = {"user_id": user.id}
            
            response = await client.post("/users/sign-in", json=sign_in_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["user"]["id"] == user.id
            assert data["learner_profile"] is not None  # Should have profile for learner
            assert data["message"] == "Successfully signed in"
    finally:
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_sign_in_user_not_found():
    """Test sign-in with non-existent user."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        sign_in_data = {"user_id": 99999}
        
        response = await client.post("/users/sign-in", json=sign_in_data)
        
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]

@pytest.mark.asyncio
async def test_get_available_roles():
    """Test getting available user roles."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/users/roles/available")
        
        assert response.status_code == 200
        roles = response.json()
        assert isinstance(roles, list)
        assert "learner" in roles
        assert "builder" in roles
        assert "curriculum_architect" in roles
        # Should not contain career roles, only profile roles
        assert "admin" in roles
        assert "developer" not in roles  # This is a career role, not profile role

@pytest.mark.asyncio
async def test_get_learner_profile_endpoint(db_session: AsyncSession):
    """Test getting learner profile via API."""
    async def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    try:
        # Create a learner user
        user_data = UserCreate(
            first_name="Student",
            current_role="learner"
        )
        user = await create_user(db_session, user_data)
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(f"/users/{user.id}/learner-profile")
            
            assert response.status_code == 200
            data = response.json()
            assert data["user_id"] == user.id
            assert data["total_content_completed"] == 0
    finally:
        app.dependency_overrides.clear()

@pytest.mark.asyncio
async def test_get_user_content_progress_endpoint(db_session: AsyncSession):
    """Test getting user content progress via API."""
    # Create a user
    user_data = UserCreate(
        first_name="Progress",
        current_role="learner"
    )
    user = await create_user(db_session, user_data)
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(f"/users/{user.id}/content-progress")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)  # Should return empty list initially