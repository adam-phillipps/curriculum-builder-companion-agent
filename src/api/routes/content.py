from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas.content import (
    LearningContentCreate, LearningContentResponse,
    AssessmentQuestionCreate, AssessmentQuestionResponse,
    PricingEstimateCreate, PricingEstimateResponse,
    LearningPathwayCreate, LearningPathwayResponse
)
from src.api.dependencies import get_db
from src.db.crud.content import (
    create_content, get_content, get_contents,
    update_content, delete_content,
    create_assessment_question, get_assessment_questions,
    create_pathway, get_pathways
)
from src.config import BuilderConstants

router = APIRouter(prefix="/api/v1", tags=["content"])

# Learning Content Routes
@router.post("/content", response_model=LearningContentResponse, status_code=status.HTTP_201_CREATED)
async def create_learning_content(
    content: LearningContentCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new learning content with metadata and relationships"""
    try:
        return await create_content(db, content)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/content/{content_id}", response_model=LearningContentResponse)
async def get_learning_content(
    content_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Retrieve specific learning content by ID"""
    content = await get_content(db, content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    return content

@router.get("/content", response_model=List[LearningContentResponse])
async def list_learning_content(
    tier: Optional[str] = Query(None, description="Filter by tier"),
    persona: Optional[str] = Query(None, description="Filter by persona"),
    content_type: Optional[str] = Query(None, description="Filter by content type"),
    status: Optional[str] = Query(None, description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List learning content with optional filters"""
    filters = {
        "tier": tier,
        "persona": persona,
        "content_type": content_type,
        "status": status
    }
    return await get_contents(db, filters, skip, limit)

@router.put("/content/{content_id}/status", response_model=LearningContentResponse)
async def update_content_status(
    content_id: int,
    status: str = Query(..., description="New status"),
    db: AsyncSession = Depends(get_db)
):
    """Update content status (e.g., draft to staged)"""
    if status not in BuilderConstants.STATES.values():
        raise HTTPException(status_code=400, detail="Invalid status")
    
    content = await get_content(db, content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    return await update_content(db, content_id, {"status": status})

# Assessment Question Routes
@router.post("/assessment-questions", response_model=AssessmentQuestionResponse)
async def create_assessment_question(
    question: AssessmentQuestionCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new assessment question"""
    try:
        return await create_assessment_question(db, question)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/assessment-questions", response_model=List[AssessmentQuestionResponse])
async def list_assessment_questions(
    tier: Optional[str] = Query(None, description="Filter by tier"),
    knowledge_area: Optional[str] = Query(None, description="Filter by knowledge area"),
    persona: Optional[str] = Query(None, description="Filter by persona"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List assessment questions with optional filters"""
    filters = {
        "tier": tier,
        "knowledge_area": knowledge_area,
        "persona": persona
    }
    return await get_assessment_questions(db, filters, skip, limit)

# Learning Pathway Routes
@router.post("/pathways", response_model=LearningPathwayResponse)
async def create_learning_pathway(
    pathway: LearningPathwayCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new learning pathway"""
    try:
        return await create_pathway(db, pathway)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/pathways", response_model=List[LearningPathwayResponse])
async def list_learning_pathways(
    target_persona: Optional[str] = Query(None, description="Filter by target persona"),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List learning pathways with optional filters"""
    filters = {"target_persona": target_persona}
    return await get_pathways(db, filters, skip, limit)

# Analysis Routes
@router.get("/analysis/coverage")
async def analyze_content_coverage(
    persona: Optional[str] = Query(None, description="Filter by persona"),
    tier: Optional[str] = Query(None, description="Filter by tier"),
    db: AsyncSession = Depends(get_db)
):
    """Analyze content coverage across personas and tiers"""
    # Implementation will be added in the analysis service
    pass

@router.get("/analysis/gaps")
async def analyze_content_gaps(
    persona: Optional[str] = Query(None, description="Filter by persona"),
    tier: Optional[str] = Query(None, description="Filter by tier"),
    db: AsyncSession = Depends(get_db)
):
    """Identify content gaps and missing prerequisites"""
    # Implementation will be added in the analysis service
    pass