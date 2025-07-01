"""
User models for the curriculum builder system.
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from src.db.database import Base

class User(Base):
    """User model for authentication and profile management."""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    email = Column(String(255), unique=True, index=True, nullable=True)
    current_role = Column(String(50), nullable=False, default="learner")
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    learner_profiles = relationship("LearnerProfile", back_populates="user")
    content_progress = relationship("UserContentProgress", back_populates="user")

class LearnerProfile(Base):
    """Learner-specific profile data and progress tracking."""
    __tablename__ = "learner_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Learning goals and objectives
    learning_goals = Column(JSON, nullable=True)  # List of goal objects
    target_outcomes = Column(JSON, nullable=True)  # List of desired outcomes
    current_pathway_id = Column(Integer, ForeignKey("learning_pathways.id"), nullable=True)
    
    # Skill assessment data
    skill_assessment = Column(JSON, nullable=True)  # Assessment results
    skill_levels = Column(JSON, nullable=True)  # Domain -> proficiency mapping
    
    # Progress tracking
    total_content_completed = Column(Integer, default=0)
    total_learning_hours = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="learner_profiles")
    current_pathway = relationship("LearningPathway", foreign_keys=[current_pathway_id])

class UserContentProgress(Base):
    """Track user progress through learning content."""
    __tablename__ = "user_content_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content_id = Column(Integer, ForeignKey("learning_content.id"), nullable=False)
    
    status = Column(String(20), nullable=False, default="not_started")  # not_started, in_progress, completed, skipped
    progress_percentage = Column(Integer, default=0)  # 0-100
    
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    last_accessed_at = Column(DateTime, default=datetime.utcnow)
    
    # Learning outcome data
    outcome_score = Column(Integer, nullable=True)  # 0-100 if assessed
    time_spent_minutes = Column(Integer, default=0)
    notes = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="content_progress")
    content = relationship("LearningContent")