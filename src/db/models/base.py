from sqlalchemy import Column, DateTime, String
from sqlalchemy.sql import func
from src.db.database import Base

class TimestampMixin:
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

class MetadataMixin:
    created_by = Column(String, nullable=True)
    updated_by = Column(String, nullable=True)
    version = Column(String, nullable=True)  # Semantic version