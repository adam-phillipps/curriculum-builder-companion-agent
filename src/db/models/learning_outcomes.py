"""
Learning outcomes models for goal tracking and pathway generation.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from src.db.database import Base

class LearningOutcome(Base):
    """Learning outcomes that users can set as goals.
    
    Learning outcomes represent specific, measurable educational objectives.
    They support AI-powered similarity search, admin approval workflows,
    and integration with personalized learning pathways.
    """
    __tablename__ = "learning_outcomes"
    
    # Core identification and content
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)  # Primary goal description (e.g., "Master Python web development")
    description = Column(Text, nullable=True)  # Detailed explanation of what learner will achieve
    
    # Categorization for filtering and discovery
    domain = Column(String(100), nullable=False, index=True)  # Learning domain (e.g., "programming", "data_science")
    difficulty_level = Column(String(20), nullable=False)  # "beginner", "intermediate", "advanced", "expert"
    tags = Column(JSON, nullable=True)  # Related technologies/concepts for similarity matching
    
    # Quality control through approval workflow
    status = Column(String(20), nullable=False, default="approved", index=True)  # "pending_approval", "approved", "rejected"
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # User-created outcomes need approval
    
    # AI/ML integration for similarity search
    embedding_vector = Column(Text, nullable=True)  # Serialized vector embedding for ChromaDB
    
    # Audit trail for tracking changes
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships for data integrity and navigation
    created_by_user = relationship("User", foreign_keys=[created_by_user_id])  # Link to creator for approval workflow
    learner_profiles = relationship("LearnerProfile", back_populates="primary_learning_outcome")  # Users who set this as primary goal
    
    def __repr__(self):
        return f"<LearningOutcome(id={self.id}, name='{self.name}', domain='{self.domain}')>"