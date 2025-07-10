"""
User API schemas for requests and responses.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict

class UserCreate(BaseModel):
    """Schema for creating a new user."""
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = None
    current_role: str = Field("learner", description="User's profile role")
    career_role: Optional[str] = Field(None, description="User's career/job role")

class UserResponse(BaseModel):
    """Schema for user data responses."""
    id: int
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    current_role: str
    career_role: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    """Schema for updating user data."""
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    email: Optional[str] = None
    current_role: Optional[str] = None
    career_role: Optional[str] = None

class LearnerProfileCreate(BaseModel):
    """Schema for creating a learner profile."""
    learning_goals: Optional[List[Dict[str, Any]]] = None
    target_outcomes: Optional[List[Dict[str, Any]]] = None
    current_pathway_id: Optional[int] = None

class LearnerProfileResponse(BaseModel):
    """Schema for learner profile responses."""
    id: int
    user_id: int
    learning_goals: Optional[List[Dict[str, Any]]]
    target_outcomes: Optional[List[Dict[str, Any]]]
    current_pathway_id: Optional[int]
    skill_assessment: Optional[Dict[str, Any]]
    skill_levels: Optional[Dict[str, Any]]
    total_content_completed: int
    total_learning_hours: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserContentProgressCreate(BaseModel):
    """Schema for creating content progress records."""
    content_id: int
    status: str = Field("not_started", description="Progress status")
    progress_percentage: int = Field(0, ge=0, le=100)

class UserContentProgressResponse(BaseModel):
    """Schema for content progress responses."""
    id: int
    user_id: int
    content_id: int
    status: str
    progress_percentage: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    last_accessed_at: datetime
    outcome_score: Optional[int]
    time_spent_minutes: int
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserSignInRequest(BaseModel):
    """Schema for simple user sign-in."""
    user_id: int = Field(..., description="User ID to sign in as")

class UserSignInByIdentifierRequest(BaseModel):
    """Schema for sign-in by email or name."""
    identifier: str = Field(..., description="Email, name, or partial match to find user")

class UserSearchRequest(BaseModel):
    """Schema for user search parameters."""
    q: Optional[str] = Field(None, description="Search query for name or email")
    role: Optional[str] = Field(None, description="Filter by user role")
    skip: int = Field(0, ge=0, description="Number of records to skip")
    limit: int = Field(100, ge=1, le=1000, description="Maximum number of records to return")

class UserSignInResponse(BaseModel):
    """Schema for sign-in response."""
    user: UserResponse
    learner_profile: Optional[LearnerProfileResponse] = None
    message: str = "Successfully signed in"