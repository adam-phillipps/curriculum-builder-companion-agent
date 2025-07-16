from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db
from src.db.crud.learning_outcomes import (
    create_learning_outcome, get_learning_outcomes, 
    update_learning_outcome_status, search_similar_outcomes,
    search_learning_outcomes_by_text
)
from src.utils.logger import get_logger, set_request_id, log_execution_time

# Create module logger
logger = get_logger("api.learning_outcomes")

router = APIRouter(prefix="/learning-outcomes", tags=["learning-outcomes"])

class LearningOutcomeCreate(BaseModel):
    name: str
    description: str
    domain: str
    difficulty_level: str
    tags: List[str] = []
    created_by_user_id: Optional[int] = None

class LearningOutcomeResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    domain: str
    difficulty_level: str
    tags: List[str]
    status: str
    created_by_user_id: Optional[int]

class OutcomeSuggestion(BaseModel):
    outcome_id: Optional[int]
    name: str
    description: str
    domain: str
    difficulty_level: str
    tags: List[str]
    similarity_score: float
    is_existing: bool

@router.get("/search", response_model=List[OutcomeSuggestion])
@log_execution_time
async def search_outcome_suggestions(
    request: Request,
    query: str = Query(..., description="User's learning goal text"),
    max_results: int = Query(10, ge=1, le=20),
    domain: Optional[str] = Query(None, description="Filter by domain"),
    db: AsyncSession = Depends(get_db)
):
    """Search for similar learning outcomes to suggest to users.
    
    This endpoint powers the learning goal autocomplete functionality.
    It uses fast database text search first, then falls back to vector
    similarity search for better matches. Always includes a custom
    goal option for user-created objectives.
    
    Args:
        query: Natural language description of learning goal
        max_results: Maximum number of suggestions to return
        domain: Optional domain filter (e.g., 'programming', 'data_science')
        db: Database session dependency
        
    Returns:
        List of outcome suggestions with similarity scores and metadata
    """
    # Set request ID for tracing
    request_id = set_request_id(request.headers.get("X-Request-ID"))
    
    logger.info(
        f"Searching for learning outcomes with query: '{query}'", 
        extra={
            "query": query, 
            "max_results": max_results,
            "domain": domain,
            "request_id": request_id
        }
    )
    
    suggestions = []
    
    try:
        # Strategy: Fast database text search first, then vector search fallback
        # This provides sub-second response times while maintaining quality
        db_outcomes = await search_learning_outcomes_by_text(
            db=db,
            query=query,
            domain=domain,
            max_results=max_results
        )
        
        logger.debug(
            f"Database search found {len(db_outcomes)} outcomes",
            extra={"db_outcome_count": len(db_outcomes), "request_id": request_id}
        )
        
        # Convert database results to suggestions with calculated similarity scores
        for outcome in db_outcomes:
            # Heuristic similarity scoring based on text matches
            # Name matches are weighted highest as they're most relevant
            name_match = query.lower() in outcome.name.lower()
            desc_match = query.lower() in (outcome.description or "").lower()
            tag_match = any(query.lower() in tag.lower() for tag in (outcome.tags or []))
            
            similarity_score = 0.3  # Base score for any database match
            if name_match: similarity_score += 0.5  # Name match is most important
            if desc_match: similarity_score += 0.2  # Description provides context
            if tag_match: similarity_score += 0.3   # Tags indicate related concepts
            
            suggestions.append(OutcomeSuggestion(
                outcome_id=outcome.id,
                name=outcome.name,
                description=outcome.description or "",
                domain=outcome.domain,
                difficulty_level=outcome.difficulty_level,
                tags=outcome.tags or [],
                similarity_score=min(similarity_score, 1.0),
                is_existing=True
            ))
        
        # Fallback to vector similarity search if database results are insufficient
        # Vector search provides semantic matching but is slower
        if len(suggestions) < 3:
            logger.debug(
                "Insufficient database results, falling back to vector search",
                extra={"suggestion_count": len(suggestions), "request_id": request_id}
            )
            try:
                similar_outcomes = await search_similar_outcomes(
                    query_text=query,
                    max_results=5,  # Limited for performance
                    domain_filter=domain
                )
                
                logger.debug(
                    f"Vector search found {len(similar_outcomes)} outcomes",
                    extra={"vector_outcome_count": len(similar_outcomes), "request_id": request_id}
                )
                
                # Add vector search results, avoiding duplicates
                existing_ids = {s.outcome_id for s in suggestions if s.outcome_id}
                
                for outcome in similar_outcomes:
                    if outcome["outcome_id"] not in existing_ids:
                        suggestions.append(OutcomeSuggestion(
                            outcome_id=outcome["outcome_id"],
                            name=outcome["name"],
                            description=outcome["description"],
                            domain=outcome["domain"],
                            difficulty_level=outcome["difficulty_level"],
                            tags=outcome["tags"],
                            similarity_score=outcome["similarity_score"],
                            is_existing=True
                        ))
            except Exception as e:
                logger.error(
                    f"Vector search fallback failed: {str(e)}",
                    extra={"error": str(e), "request_id": request_id},
                    exc_info=True
                )
                # Continue without vector results
    
    except Exception as e:
        logger.error(
            f"Database search error: {str(e)}",
            extra={"error": str(e), "request_id": request_id},
            exc_info=True
        )
        # Try vector search as complete fallback
        try:
            similar_outcomes = await search_similar_outcomes(
                query_text=query,
                max_results=max_results - 1,
                domain_filter=domain
            )
            
            for outcome in similar_outcomes:
                suggestions.append(OutcomeSuggestion(
                    outcome_id=outcome["outcome_id"],
                    name=outcome["name"],
                    description=outcome["description"],
                    domain=outcome["domain"],
                    difficulty_level=outcome["difficulty_level"],
                    tags=outcome["tags"],
                    similarity_score=outcome["similarity_score"],
                    is_existing=True
                ))
        except Exception as ve:
            logger.error(
                f"Vector search also failed: {str(ve)}",
                extra={"error": str(ve), "request_id": request_id},
                exc_info=True
            )
            # Continue to custom suggestion
    
    # Always provide option to create custom learning outcome
    # This ensures users can always proceed even if no good matches exist
    suggestions.append(OutcomeSuggestion(
        outcome_id=None,
        name=query,
        description=f"Custom learning goal: {query}",
        domain="custom",
        difficulty_level="intermediate",  # Default difficulty for user-created goals
        tags=[],
        similarity_score=0.0,  # Custom options have no similarity score
        is_existing=False  # Indicates this will create a new outcome
    ))
    
    # Sort by similarity score (highest first) and limit results
    # Custom option will appear last due to 0.0 similarity score
    suggestions.sort(key=lambda x: x.similarity_score, reverse=True)
    final_suggestions = suggestions[:max_results]
    
    logger.info(
        f"Returning {len(final_suggestions)} learning outcome suggestions",
        extra={
            "suggestion_count": len(final_suggestions),
            "has_custom_option": any(not s.is_existing for s in final_suggestions),
            "request_id": request_id
        }
    )
    
    return final_suggestions

@router.post("", response_model=LearningOutcomeResponse, status_code=201)
@log_execution_time
async def create_outcome(
    request: Request,
    outcome: LearningOutcomeCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new learning outcome (requires admin approval if created by user)."""
    # Set request ID for tracing
    request_id = set_request_id(request.headers.get("X-Request-ID"))
    
    logger.info(
        f"Creating new learning outcome: '{outcome.name}'",
        extra={
            "outcome_name": outcome.name,
            "domain": outcome.domain,
            "difficulty_level": outcome.difficulty_level,
            "created_by_user_id": outcome.created_by_user_id,
            "request_id": request_id
        }
    )
    
    status = "approved" if not outcome.created_by_user_id else "pending_approval"
    
    try:
        db_outcome = await create_learning_outcome(
            db=db,
            name=outcome.name,
            description=outcome.description,
            domain=outcome.domain,
            difficulty_level=outcome.difficulty_level,
            tags=outcome.tags,
            created_by_user_id=outcome.created_by_user_id,
            status=status
        )
        
        logger.info(
            f"Successfully created learning outcome with ID {db_outcome.id}",
            extra={
                "outcome_id": db_outcome.id,
                "status": db_outcome.status,
                "request_id": request_id
            }
        )
    except Exception as e:
        logger.error(
            f"Failed to create learning outcome: {str(e)}",
            extra={"error": str(e), "request_id": request_id},
            exc_info=True
        )
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create learning outcome: {str(e)}"
        )
    
    return LearningOutcomeResponse(
        id=db_outcome.id,
        name=db_outcome.name,
        description=db_outcome.description,
        domain=db_outcome.domain,
        difficulty_level=db_outcome.difficulty_level,
        tags=db_outcome.tags or [],
        status=db_outcome.status,
        created_by_user_id=db_outcome.created_by_user_id
    )

@router.get("", response_model=List[LearningOutcomeResponse])
async def list_outcomes(
    status: Optional[str] = Query(None, description="Filter by status"),
    domain: Optional[str] = Query(None, description="Filter by domain"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List learning outcomes with optional filters."""
    outcomes = await get_learning_outcomes(
        db=db,
        status=status,
        domain=domain,
        skip=skip,
        limit=limit
    )
    
    return [
        LearningOutcomeResponse(
            id=outcome.id,
            name=outcome.name,
            description=outcome.description,
            domain=outcome.domain,
            difficulty_level=outcome.difficulty_level,
            tags=outcome.tags or [],
            status=outcome.status,
            created_by_user_id=outcome.created_by_user_id
        )
        for outcome in outcomes
    ]

# Admin-only routes
@router.get("/admin/pending", response_model=List[LearningOutcomeResponse])
async def get_pending_outcomes(
    db: AsyncSession = Depends(get_db)
):
    """Get outcomes pending admin approval."""
    outcomes = await get_learning_outcomes(
        db=db,
        status="pending_approval",
        skip=0,
        limit=100
    )
    
    return [
        LearningOutcomeResponse(
            id=outcome.id,
            name=outcome.name,
            description=outcome.description,
            domain=outcome.domain,
            difficulty_level=outcome.difficulty_level,
            tags=outcome.tags or [],
            status=outcome.status,
            created_by_user_id=outcome.created_by_user_id
        )
        for outcome in outcomes
    ]

@router.put("/admin/{outcome_id}/approve")
async def approve_outcome(
    outcome_id: int,
    approve: bool = Query(True, description="True to approve, False to reject"),
    db: AsyncSession = Depends(get_db)
):
    """Approve or reject a pending learning outcome."""
    status = "approved" if approve else "rejected"
    
    outcome = await update_learning_outcome_status(
        db=db,
        outcome_id=outcome_id,
        status=status
    )
    
    if not outcome:
        raise HTTPException(status_code=404, detail="Learning outcome not found")
    
    return {"message": f"Outcome {status}", "outcome_id": outcome_id}