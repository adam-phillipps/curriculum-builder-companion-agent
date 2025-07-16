from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from src.db.models.learning_outcomes import LearningOutcome
from src.services.vector_store import vector_store
from src.utils.logger import get_logger, log_execution_time

# Create module logger
logger = get_logger("db.crud.learning_outcomes")

@log_execution_time
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
    
    logger.info(
        f"Creating learning outcome in database: '{name}'",
        extra={
            "outcome_name": name,
            "domain": domain,
            "difficulty_level": difficulty_level,
            "status": status,
            "created_by_user_id": created_by_user_id
        }
    )
    
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
    try:
        await db.commit()
        await db.refresh(outcome)
        logger.info(
            f"Successfully committed learning outcome to database with ID {outcome.id}",
            extra={"outcome_id": outcome.id}
        )
    except Exception as e:
        logger.error(
            f"Failed to commit learning outcome to database: {str(e)}",
            extra={"error": str(e)},
            exc_info=True
        )
        raise
    
    # Add to vector store (non-blocking)
    try:
        logger.debug(
            f"Adding learning outcome ID {outcome.id} to vector store",
            extra={"outcome_id": outcome.id}
        )
        vector_store.add_learning_outcome(
            outcome_id=outcome.id,
            name=outcome.name,
            description=outcome.description or "",
            domain=outcome.domain,
            difficulty_level=outcome.difficulty_level,
            tags=outcome.tags or []
        )
        logger.debug(
            f"Successfully added learning outcome ID {outcome.id} to vector store",
            extra={"outcome_id": outcome.id}
        )
    except Exception as e:
        logger.error(
            f"Failed to add outcome to vector store: {str(e)}",
            extra={"error": str(e), "outcome_id": outcome.id},
            exc_info=True
        )
        # Continue without vector store - not critical for creation
    
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

@log_execution_time
async def search_similar_outcomes(
    query_text: str,
    max_results: int = 10,
    domain_filter: Optional[str] = None
) -> List[Dict[str, Any]]:
    """Search for similar learning outcomes using vector similarity."""
    logger.info(
        f"Searching for similar outcomes with vector store: '{query_text}'",
        extra={
            "query_text": query_text,
            "max_results": max_results,
            "domain_filter": domain_filter
        }
    )
    
    try:
        results = vector_store.find_similar_outcomes(
            query_text=query_text,
            max_results=max_results,
            domain_filter=domain_filter
        )
        
        logger.info(
            f"Vector search found {len(results)} similar outcomes",
            extra={"result_count": len(results)}
        )
        return results
    except Exception as e:
        logger.error(
            f"Error searching similar outcomes: {str(e)}",
            extra={"error": str(e)},
            exc_info=True
        )
        return []

@log_execution_time
async def search_learning_outcomes_by_text(
    db: AsyncSession,
    query: str,
    domain: Optional[str] = None,
    max_results: int = 10
) -> List[LearningOutcome]:
    """Search learning outcomes by text in name and description."""
    logger.info(
        f"Searching learning outcomes by text: '{query}'",
        extra={
            "query": query,
            "domain": domain,
            "max_results": max_results
        }
    )
    
    try:
        db_query = select(LearningOutcome).where(
            LearningOutcome.status == "approved"
        )
        
        # Text-based similarity using ILIKE for fast matching
        search_conditions = [
            LearningOutcome.name.ilike(f"%{query}%"),
            LearningOutcome.description.ilike(f"%{query}%")
        ]
        
        if domain:
            search_conditions.append(LearningOutcome.domain == domain)
        
        db_query = db_query.where(or_(*search_conditions)).limit(max_results)
        
        result = await db.execute(db_query)
        outcomes = result.scalars().all()
        
        logger.info(
            f"Database text search found {len(outcomes)} outcomes",
            extra={"result_count": len(outcomes)}
        )
        
        return outcomes
        
    except Exception as e:
        logger.error(
            f"Error in text search: {str(e)}",
            extra={"error": str(e)},
            exc_info=True
        )
        return []