"""
Learning outcomes models for goal tracking and pathway generation.
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from src.db.database import Base

class LearningOutcome(Base):
    """Learning outcomes that users can set as goals."""
    __tablename__ = "learning_outcomes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    domain = Column(String(100), nullable=False, index=True)
    difficulty_level = Column(String(20), nullable=False)  # beginner, intermediate, advanced, expert
    tags = Column(JSON, nullable=True)  # Array of related tags for similarity matching
    
    # Approval workflow
    status = Column(String(20), nullable=False, default="approved", index=True)  # pending_approval, approved, rejected
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Vector embedding for similarity search
    embedding_vector = Column(Text, nullable=True)  # Serialized embedding
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    created_by_user = relationship("User", foreign_keys=[created_by_user_id])
    learner_profiles = relationship("LearnerProfile", back_populates="primary_learning_outcome")
    
    def __repr__(self):
        return f"<LearningOutcome(id={self.id}, name='{self.name}', domain='{self.domain}')>"