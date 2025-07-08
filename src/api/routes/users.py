"""
User management API routes.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db
from src.api.schemas.user import (
    UserCreate, UserResponse, UserUpdate, UserSignInRequest, UserSignInResponse,
    LearnerProfileResponse, UserContentProgressResponse
)
from src.db.crud.user import (
    create_user, get_user, get_users, update_user,
    get_learner_profile, get_user_content_progress
)
from src.config import BuilderConstants

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_new_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """Create a new user account."""
    # Validate profile role
    valid_roles = BuilderConstants.APPLICATION_ROLES.get_names()
    if user_data.current_role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid profile role. Must be one of: {valid_roles}"
        )
    
    try:
        user = await create_user(db, user_data)
        return UserResponse.model_validate(user)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create user: {str(e)}"
        )

@router.get("/", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
) -> List[UserResponse]:
    """Get list of users."""
    users = await get_users(db, skip=skip, limit=limit)
    return [UserResponse.model_validate(user) for user in users]

@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(
    user_id: int,
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """Get user by ID."""
    user = await get_user(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserResponse.model_validate(user)

@router.put("/{user_id}", response_model=UserResponse)
async def update_user_by_id(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db)
) -> UserResponse:
    """Update user data."""
    # Validate profile role if provided
    if user_data.current_role:
        valid_roles = BuilderConstants.APPLICATION_ROLES.get_names()
        if user_data.current_role not in valid_roles:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid profile role. Must be one of: {valid_roles}"
            )
    
    user = await update_user(db, user_id, user_data)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return UserResponse.model_validate(user)

@router.post("/sign-in", response_model=UserSignInResponse)
async def sign_in_user(
    sign_in_data: UserSignInRequest,
    db: AsyncSession = Depends(get_db)
) -> UserSignInResponse:
    """Simple user sign-in (no authentication for now)."""
    user = await get_user(db, sign_in_data.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    learner_profile = None
    if user.current_role == "learner":
        learner_profile = await get_learner_profile(db, user.id)
    
    return UserSignInResponse(
        user=UserResponse.model_validate(user),
        learner_profile=LearnerProfileResponse.model_validate(learner_profile) if learner_profile else None
    )

@router.get("/{user_id}/learner-profile", response_model=LearnerProfileResponse)
async def get_user_learner_profile(
    user_id: int,
    db: AsyncSession = Depends(get_db)
) -> LearnerProfileResponse:
    """Get learner profile for a user."""
    profile = await get_learner_profile(db, user_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Learner profile not found"
        )
    return LearnerProfileResponse.model_validate(profile)

@router.get("/{user_id}/content-progress", response_model=List[UserContentProgressResponse])
async def get_user_progress(
    user_id: int,
    db: AsyncSession = Depends(get_db)
) -> List[UserContentProgressResponse]:
    """Get content progress for a user."""
    progress_records = await get_user_content_progress(db, user_id)
    return [UserContentProgressResponse.model_validate(record) for record in progress_records]

@router.get("/roles/available", response_model=List[str])
async def get_available_roles() -> List[str]:
    """Get list of available profile roles."""
    return BuilderConstants.APPLICATION_ROLES.get_names()

@router.get("/career-roles/available", response_model=List[str])
async def get_available_career_roles() -> List[str]:
    """Get list of available career/job roles."""
    return BuilderConstants.PERSONAS.get_names()