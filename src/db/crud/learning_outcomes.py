from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from src.db.models.learning_outcomes import LearningOutcome
from src.services.vector_store import vector_store

async def create_learning_outcome(
    db: AsyncSession,
    name: str,
    description: str,
    domain: str,
    difficulty_level: str,
    tags: List[str] = None,
    created_by_user_id: Optional[int] = None,
    status: str = "approved"
) -> LearningOutcome:
    """Create new learning outcome and add to vector store."""
    
    outcome = LearningOutcome(
        name=name,
        description=description,
        domain=domain,
        difficulty_level=difficulty_level,
        tags=tags or [],
        status=status,
        created_by_user_id=created_by_user_id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    db.add(outcome)
    await db.commit()
    await db.refresh(outcome)
    
    # Add to vector store
    try:
        vector_store.add_learning_outcome(
            outcome_id=outcome.id,
            name=outcome.name,
            description=outcome.description or "",
            domain=outcome.domain,
            difficulty_level=outcome.difficulty_level,
            tags=outcome.tags or []
        )
    except Exception as e:
        print(f"Failed to add outcome to vector store: {e}")
    
    return outcome

async def get_learning_outcome(
    db: AsyncSession,
    outcome_id: int
) -> Optional[LearningOutcome]:
    """Get learning outcome by ID."""
    result = await db.execute(
        select(LearningOutcome).where(LearningOutcome.id == outcome_id)
    )
    return result.scalar_one_or_none()

async def get_learning_outcomes(
    db: AsyncSession,
    status: Optional[str] = None,
    domain: Optional[str] = None,
    skip: int = 0,
    limit: int = 100
) -> List[LearningOutcome]:
    """Get learning outcomes with optional filters."""
    query = select(LearningOutcome)
    
    conditions = []
    if status:
        conditions.append(LearningOutcome.status == status)
    if domain:
        conditions.append(LearningOutcome.domain == domain)
    
    if conditions:
        query = query.where(and_(*conditions))
    
    query = query.offset(skip).limit(limit).order_by(LearningOutcome.created_at.desc())
    
    result = await db.execute(query)
    return result.scalars().all()

async def update_learning_outcome_status(
    db: AsyncSession,
    outcome_id: int,
    status: str,
    admin_user_id: Optional[int] = None
) -> Optional[LearningOutcome]:
    """Update learning outcome status (approve/reject)."""
    outcome = await get_learning_outcome(db, outcome_id)
    if not outcome:
        return None
    
    outcome.status = status
    outcome.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(outcome)
    
    return outcome

async def search_similar_outcomes(
    query_text: str,
    max_results: int = 10,
    domain_filter: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Search for similar learning outcomes using vector similarity."""
    try:
        return vector_store.find_similar_outcomes(
            query_text=query_text,
            max_results=max_results,
            domain_filter=domain_filter
        )
    except Exception as e:
        print(f"Error searching similar outcomes: {e}")
        return []