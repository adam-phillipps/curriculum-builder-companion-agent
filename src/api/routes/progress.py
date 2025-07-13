from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from src.api.dependencies import get_db
from src.db.models.user import UserContentProgress
from src.db.models.content import LearningContent
from sqlalchemy import select

router = APIRouter(prefix="/progress", tags=["progress"])

class EnrollRequest(BaseModel):
    user_id: int
    content_id: int

class ProgressUpdateRequest(BaseModel):
    user_id: int
    content_id: int
    comprehension_percentage: Optional[float] = None
    status: Optional[str] = None

class ProgressResponse(BaseModel):
    id: int
    user_id: int
    content_id: int
    status: str
    progress_percentage: int
    comprehension_percentage: Optional[float]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

@router.post("/enroll", response_model=ProgressResponse)
async def enroll_in_content(
    request: EnrollRequest,
    db: AsyncSession = Depends(get_db)
):
    """Enroll user in learning content."""
    # Check if content exists
    content_result = await db.execute(
        select(LearningContent).where(LearningContent.id == request.content_id)
    )
    content = content_result.scalar_one_or_none()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    # Check if already enrolled
    existing_result = await db.execute(
        select(UserContentProgress).where(
            UserContentProgress.user_id == request.user_id,
            UserContentProgress.content_id == request.content_id
        )
    )
    existing = existing_result.scalar_one_or_none()
    
    if existing:
        return ProgressResponse(
            id=existing.id,
            user_id=existing.user_id,
            content_id=existing.content_id,
            status=existing.status,
            progress_percentage=existing.progress_percentage,
            comprehension_percentage=existing.comprehension_percentage,
            started_at=existing.started_at,
            completed_at=existing.completed_at
        )
    
    # Create new progress record
    progress = UserContentProgress(
        user_id=request.user_id,
        content_id=request.content_id,
        status="in_progress",
        progress_percentage=0,
        comprehension_percentage=0.0,
        started_at=datetime.utcnow()
    )
    
    db.add(progress)
    await db.commit()
    await db.refresh(progress)
    
    return ProgressResponse(
        id=progress.id,
        user_id=progress.user_id,
        content_id=progress.content_id,
        status=progress.status,
        progress_percentage=progress.progress_percentage,
        comprehension_percentage=progress.comprehension_percentage,
        started_at=progress.started_at,
        completed_at=progress.completed_at
    )

@router.put("/update", response_model=ProgressResponse)
async def update_progress(
    request: ProgressUpdateRequest,
    db: AsyncSession = Depends(get_db)
):
    """Update user progress on learning content."""
    # Find existing progress record
    result = await db.execute(
        select(UserContentProgress).where(
            UserContentProgress.user_id == request.user_id,
            UserContentProgress.content_id == request.content_id
        )
    )
    progress = result.scalar_one_or_none()
    
    if not progress:
        raise HTTPException(status_code=404, detail="Progress record not found")
    
    # Update fields
    if request.comprehension_percentage is not None:
        progress.comprehension_percentage = request.comprehension_percentage
    
    if request.status is not None:
        progress.status = request.status
        if request.status == "completed":
            progress.completed_at = datetime.utcnow()
            progress.progress_percentage = 100
    
    progress.last_accessed_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(progress)
    
    return ProgressResponse(
        id=progress.id,
        user_id=progress.user_id,
        content_id=progress.content_id,
        status=progress.status,
        progress_percentage=progress.progress_percentage,
        comprehension_percentage=progress.comprehension_percentage,
        started_at=progress.started_at,
        completed_at=progress.completed_at
    )

@router.get("/{user_id}/{content_id}", response_model=ProgressResponse)
async def get_progress(
    user_id: int,
    content_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get user progress for specific content."""
    result = await db.execute(
        select(UserContentProgress).where(
            UserContentProgress.user_id == user_id,
            UserContentProgress.content_id == content_id
        )
    )
    progress = result.scalar_one_or_none()
    
    if not progress:
        raise HTTPException(status_code=404, detail="Progress record not found")
    
    return ProgressResponse(
        id=progress.id,
        user_id=progress.user_id,
        content_id=progress.content_id,
        status=progress.status,
        progress_percentage=progress.progress_percentage,
        comprehension_percentage=progress.comprehension_percentage,
        started_at=progress.started_at,
        completed_at=progress.completed_at
    )