from typing import Dict, List, Optional, Any
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.db.models.content import (
    LearningContent,
    AssessmentQuestion,
    LearningPathway,
    PathwayItem,
    PricingEstimate
)
from src.api.schemas.content import (
    LearningContentCreate,
    AssessmentQuestionCreate,
    LearningPathwayCreate,
    PricingEstimateCreate
)

# Learning Content CRUD
async def create_content(
    db: AsyncSession,
    content: LearningContentCreate
) -> LearningContent:
    """Create new learning content with relationships"""
    db_content = LearningContent(
        code_title=content.code_title,
        title=content.title,
        description=content.description,
        content_type=content.content_type,
        tier=content.tier,
        personas=content.personas,
        learning_objectives=content.learning_objectives,
        estimated_duration=content.estimated_duration,
        sandbox_type=content.sandbox_type,
        aws_services=content.aws_services,
        technical_requirements=content.technical_requirements,
        estimated_cost=content.estimated_cost,
        cost_breakdown=content.cost_breakdown,
        status=content.status,
        tags=content.tags,
        notes=content.notes
    )

    # Add prerequisites if specified
    if content.prerequisite_ids:
        prerequisites = await db.execute(
            select(LearningContent).where(
                LearningContent.id.in_(content.prerequisite_ids)
            )
        )
        db_content.prerequisites.extend(prerequisites.scalars().all())

    # Add assessment questions if specified
    if content.assessment_question_ids:
        questions = await db.execute(
            select(AssessmentQuestion).where(
                AssessmentQuestion.id.in_(content.assessment_question_ids)
            )
        )
        db_content.assessment_questions.extend(questions.scalars().all())

    db.add(db_content)
    await db.commit()
    await db.refresh(db_content)
    return db_content

async def get_content(
    db: AsyncSession,
    content_id: int
) -> Optional[LearningContent]:
    """Retrieve specific learning content by ID"""
    query = select(LearningContent).options(
        joinedload(LearningContent.prerequisites),
        joinedload(LearningContent.assessment_questions),
        joinedload(LearningContent.pricing_estimates)
    ).where(LearningContent.id == content_id)
    
    result = await db.execute(query)
    return result.scalars().unique().first()

async def get_contents(
    db: AsyncSession,
    filters: Dict[str, Any],
    skip: int = 0,
    limit: int = 10
) -> List[LearningContent]:
    """List learning content with filters"""
    query = select(LearningContent).options(
        joinedload(LearningContent.prerequisites),
        joinedload(LearningContent.assessment_questions)
    )

    # Apply filters
    conditions = []
    if filters.get("tier"):
        conditions.append(LearningContent.tier == filters["tier"])
    if filters.get("persona"):
        conditions.append(LearningContent.personas.contains(filters["persona"]))
    if filters.get("content_type"):
        conditions.append(LearningContent.content_type == filters["content_type"])
    if filters.get("status"):
        conditions.append(LearningContent.status == filters["status"])

    if conditions:
        query = query.where(and_(*conditions))

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().unique().all()

async def update_content(
    db: AsyncSession,
    content_id: int,
    updates: Dict[str, Any]
) -> Optional[LearningContent]:
    """Update learning content"""
    content = await get_content(db, content_id)
    if not content:
        return None

    for key, value in updates.items():
        setattr(content, key, value)

    await db.commit()
    await db.refresh(content)
    return content

async def delete_content(
    db: AsyncSession,
    content_id: int
) -> bool:
    """Delete learning content"""
    content = await get_content(db, content_id)
    if not content:
        return False

    await db.delete(content)
    await db.commit()
    return True

# Assessment Question CRUD
async def create_assessment_question(
    db: AsyncSession,
    question: AssessmentQuestionCreate
) -> AssessmentQuestion:
    """Create new assessment question"""
    db_question = AssessmentQuestion(**question.model_dump())
    db.add(db_question)
    await db.commit()
    await db.refresh(db_question)
    return db_question

async def get_assessment_questions(
    db: AsyncSession,
    filters: Dict[str, Any],
    skip: int = 0,
    limit: int = 10
) -> List[AssessmentQuestion]:
    """List assessment questions with filters"""
    query = select(AssessmentQuestion).options(
        joinedload(AssessmentQuestion.related_content)
    )

    # Apply filters
    conditions = []
    if filters.get("tier"):
        conditions.append(AssessmentQuestion.difficulty_tier == filters["tier"])
    if filters.get("knowledge_area"):
        conditions.append(AssessmentQuestion.knowledge_area == filters["knowledge_area"])
    if filters.get("persona"):
        conditions.append(AssessmentQuestion.personas.contains(filters["persona"]))

    if conditions:
        query = query.where(and_(*conditions))

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().unique().all()

# Learning Pathway CRUD
async def create_pathway(
    db: AsyncSession,
    pathway: LearningPathwayCreate
) -> LearningPathway:
    """Create new learning pathway"""
    db_pathway = LearningPathway(
        name=pathway.name,
        description=pathway.description,
        target_persona=pathway.target_persona,
        estimated_duration=pathway.estimated_duration,
        total_cost=pathway.total_cost
    )

    # Add pathway items directly to the relationship
    for item in pathway.items:
        db_item = PathwayItem(
            content_id=item.content_id,
            sequence=item.sequence
        )
        db_pathway.items.append(db_item)

    db.add(db_pathway)
    await db.commit()
    await db.refresh(db_pathway)
    
    # Eagerly load the items to avoid lazy loading issues
    result = await db.execute(
        select(LearningPathway)
        .options(joinedload(LearningPathway.items))
        .where(LearningPathway.id == db_pathway.id)
    )
    return result.scalars().unique().first()

async def get_pathways(
    db: AsyncSession,
    filters: Dict[str, Any],
    skip: int = 0,
    limit: int = 10
) -> List[LearningPathway]:
    """List learning pathways with filters"""
    query = select(LearningPathway).options(
        joinedload(LearningPathway.items).joinedload(PathwayItem.content)
    )

    if filters.get("target_persona"):
        query = query.where(LearningPathway.target_persona == filters["target_persona"])

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    return result.scalars().unique().all()
