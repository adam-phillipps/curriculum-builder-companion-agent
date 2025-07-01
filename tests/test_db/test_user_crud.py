"""
Tests for user CRUD operations.
"""
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.crud.user import (
    create_user, get_user, get_users, update_user,
    create_learner_profile, get_learner_profile
)
from src.api.schemas.user import UserCreate, UserUpdate, LearnerProfileCreate

@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession):
    """Test creating a new user."""
    user_data = UserCreate(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        current_role="learner"
    )
    
    user = await create_user(db_session, user_data)
    
    assert user.id is not None
    assert user.first_name == "John"
    assert user.last_name == "Doe"
    assert user.email == "john.doe@example.com"
    assert user.current_role == "learner"
    assert user.is_active is True

@pytest.mark.asyncio
async def test_create_user_creates_learner_profile(db_session: AsyncSession):
    """Test that creating a learner user also creates a learner profile."""
    user_data = UserCreate(
        first_name="Jane",
        last_name="Smith",
        current_role="learner"
    )
    
    user = await create_user(db_session, user_data)
    profile = await get_learner_profile(db_session, user.id)
    
    assert profile is not None
    assert profile.user_id == user.id
    assert profile.total_content_completed == 0
    assert profile.total_learning_hours == 0

@pytest.mark.asyncio
async def test_get_user(db_session: AsyncSession):
    """Test getting a user by ID."""
    user_data = UserCreate(
        first_name="Alice",
        last_name="Johnson",
        current_role="developer"
    )
    
    created_user = await create_user(db_session, user_data)
    retrieved_user = await get_user(db_session, created_user.id)
    
    assert retrieved_user is not None
    assert retrieved_user.id == created_user.id
    assert retrieved_user.first_name == "Alice"

@pytest.mark.asyncio
async def test_get_user_not_found(db_session: AsyncSession):
    """Test getting a non-existent user."""
    user = await get_user(db_session, 99999)
    assert user is None

@pytest.mark.asyncio
async def test_get_users(db_session: AsyncSession):
    """Test getting list of users."""
    # Create multiple users
    for i in range(3):
        user_data = UserCreate(
            first_name=f"User{i}",
            current_role="learner"
        )
        await create_user(db_session, user_data)
    
    users = await get_users(db_session, skip=0, limit=10)
    assert len(users) >= 3

@pytest.mark.asyncio
async def test_update_user(db_session: AsyncSession):
    """Test updating user data."""
    user_data = UserCreate(
        first_name="Bob",
        current_role="learner"
    )
    
    user = await create_user(db_session, user_data)
    
    update_data = UserUpdate(
        first_name="Robert",
        last_name="Wilson",
        current_role="developer"
    )
    
    updated_user = await update_user(db_session, user.id, update_data)
    
    assert updated_user is not None
    assert updated_user.first_name == "Robert"
    assert updated_user.last_name == "Wilson"
    assert updated_user.current_role == "developer"

@pytest.mark.asyncio
async def test_update_user_not_found(db_session: AsyncSession):
    """Test updating a non-existent user."""
    update_data = UserUpdate(first_name="Nobody")
    updated_user = await update_user(db_session, 99999, update_data)
    assert updated_user is None

@pytest.mark.asyncio
async def test_create_learner_profile(db_session: AsyncSession):
    """Test creating a learner profile."""
    user_data = UserCreate(
        first_name="Learner",
        current_role="developer"  # Not learner, so no auto-profile
    )
    
    user = await create_user(db_session, user_data)
    
    profile_data = LearnerProfileCreate(
        learning_goals=[{"goal": "Learn Python", "priority": "high"}],
        target_outcomes=[{"outcome": "Build web app", "deadline": "2024-12-31"}]
    )
    
    profile = await create_learner_profile(db_session, user.id, profile_data)
    
    assert profile.user_id == user.id
    assert profile.learning_goals == [{"goal": "Learn Python", "priority": "high"}]
    assert profile.target_outcomes == [{"outcome": "Build web app", "deadline": "2024-12-31"}]

@pytest.mark.asyncio
async def test_get_learner_profile(db_session: AsyncSession):
    """Test getting a learner profile."""
    user_data = UserCreate(
        first_name="Student",
        current_role="learner"
    )
    
    user = await create_user(db_session, user_data)
    profile = await get_learner_profile(db_session, user.id)
    
    assert profile is not None
    assert profile.user_id == user.id

@pytest.mark.asyncio
async def test_get_learner_profile_not_found(db_session: AsyncSession):
    """Test getting a non-existent learner profile."""
    profile = await get_learner_profile(db_session, 99999)
    assert profile is None