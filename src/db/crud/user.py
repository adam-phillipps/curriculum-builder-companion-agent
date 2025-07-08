"""
CRUD operations for user management.
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.orm import selectinload

from src.db.models.user import User, LearnerProfile, UserContentProgress
from src.api.schemas.user import UserCreate, UserUpdate, LearnerProfileCreate, UserContentProgressCreate

async def create_user(db: AsyncSession, user_data: UserCreate) -> User:
    """Create a new user."""
    user = User(**user_data.model_dump())
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Create learner profile if role is learner
    if user.current_role == "learner":
        await create_learner_profile(db, user.id, LearnerProfileCreate())
    
    return user

async def get_user(db: AsyncSession, user_id: int) -> Optional[User]:
    """Get user by ID."""
    result = await db.execute(
        select(User)
        .options(selectinload(User.learner_profiles))
        .where(User.id == user_id)
    )
    return result.scalar_one_or_none()

async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
    """Get list of users."""
    result = await db.execute(
        select(User)
        .offset(skip)
        .limit(limit)
        .order_by(User.created_at.desc())
    )
    return result.scalars().all()

async def search_users(
    db: AsyncSession, 
    search_query: Optional[str] = None,
    role: Optional[str] = None,
    skip: int = 0, 
    limit: int = 100
) -> List[User]:
    """Search users by name, email, or role with flexible criteria."""
    query = select(User)
    
    # Add search filters
    if search_query:
        search_filter = or_(
            User.first_name.ilike(f"%{search_query}%"),
            User.last_name.ilike(f"%{search_query}%"),
            User.email.ilike(f"%{search_query}%")
        )
        query = query.where(search_filter)
    
    if role:
        query = query.where(User.current_role == role)
    
    query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
    
    result = await db.execute(query)
    return result.scalars().all()

async def find_user_by_identifier(db: AsyncSession, identifier: str) -> Optional[User]:
    """Find user by email or name for sign-in purposes."""
    # First try exact matches
    result = await db.execute(
        select(User).where(
            or_(
                User.email == identifier,
                User.first_name == identifier,
                User.last_name == identifier,
                (User.first_name + ' ' + User.last_name) == identifier
            )
        ).limit(1)
    )
    user = result.scalar_one_or_none()
    
    # If no exact match, try partial matches
    if not user:
        result = await db.execute(
            select(User).where(
                or_(
                    User.email.ilike(f"%{identifier}%"),
                    User.first_name.ilike(f"%{identifier}%"),
                    User.last_name.ilike(f"%{identifier}%"),
                    (User.first_name + ' ' + User.last_name).ilike(f"%{identifier}%")
                )
            ).order_by(User.created_at.desc()).limit(1)
        )
        user = result.scalar_one_or_none()
    
    return user

async def update_user(db: AsyncSession, user_id: int, user_data: UserUpdate) -> Optional[User]:
    """Update user data."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        return None
    
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    await db.commit()
    await db.refresh(user)
    return user

async def create_learner_profile(db: AsyncSession, user_id: int, profile_data: LearnerProfileCreate) -> LearnerProfile:
    """Create a learner profile for a user."""
    profile = LearnerProfile(
        user_id=user_id,
        **profile_data.model_dump()
    )
    db.add(profile)
    await db.commit()
    await db.refresh(profile)
    return profile

async def get_learner_profile(db: AsyncSession, user_id: int) -> Optional[LearnerProfile]:
    """Get learner profile for a user."""
    result = await db.execute(
        select(LearnerProfile)
        .where(LearnerProfile.user_id == user_id)
        .order_by(LearnerProfile.created_at.desc())
    )
    return result.scalar_one_or_none()

async def update_learner_profile(db: AsyncSession, user_id: int, profile_data: Dict[str, Any]) -> Optional[LearnerProfile]:
    """Update learner profile."""
    result = await db.execute(
        select(LearnerProfile).where(LearnerProfile.user_id == user_id)
    )
    profile = result.scalar_one_or_none()
    
    if not profile:
        return None
    
    for field, value in profile_data.items():
        if hasattr(profile, field):
            setattr(profile, field, value)
    
    await db.commit()
    await db.refresh(profile)
    return profile

async def create_content_progress(db: AsyncSession, user_id: int, progress_data: UserContentProgressCreate) -> UserContentProgress:
    """Create or update user content progress."""
    # Check if progress already exists
    result = await db.execute(
        select(UserContentProgress)
        .where(
            UserContentProgress.user_id == user_id,
            UserContentProgress.content_id == progress_data.content_id
        )
    )
    existing_progress = result.scalar_one_or_none()
    
    if existing_progress:
        # Update existing progress
        for field, value in progress_data.model_dump().items():
            setattr(existing_progress, field, value)
        await db.commit()
        await db.refresh(existing_progress)
        return existing_progress
    else:
        # Create new progress record
        progress = UserContentProgress(
            user_id=user_id,
            **progress_data.model_dump()
        )
        db.add(progress)
        await db.commit()
        await db.refresh(progress)
        return progress

async def get_user_content_progress(db: AsyncSession, user_id: int) -> List[UserContentProgress]:
    """Get all content progress for a user."""
    result = await db.execute(
        select(UserContentProgress)
        .options(selectinload(UserContentProgress.content))
        .where(UserContentProgress.user_id == user_id)
        .order_by(UserContentProgress.last_accessed_at.desc())
    )
    return result.scalars().all()