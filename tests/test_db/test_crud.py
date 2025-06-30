import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.crud.content import (
    create_content,
    get_content,
    get_contents,
    update_content,
    delete_content,
    create_assessment_question,
    get_assessment_questions,
    create_pathway,
    get_pathways
)
from src.api.schemas.content import (
    LearningContentCreate,
    AssessmentQuestionCreate,
    PathwayItemCreate,
    LearningPathwayCreate
)
from src.config import BuilderConstants

@pytest.fixture
def content_create_data():
    import random
    return {
        "code_title": f"T2.DEV.{random.randint(100, 999):03d}",
        "title": "Introduction to AWS Lambda",
        "description": "Learn the basics of serverless computing with AWS Lambda",
        "content_type": BuilderConstants.CONTENT_TYPES.LESSON.name,
        "tier": BuilderConstants.TIERS.T2.name,
        "personas": [BuilderConstants.PERSONAS.DEV.name],
        "learning_objectives": ["Understand serverless architecture", "Deploy Lambda functions"],
        "estimated_duration": 60,
        "sandbox_type": BuilderConstants.SANDBOX_TYPES.INDIVIDUAL.name,
        "aws_services": ["Lambda", "IAM"],
        "technical_requirements": {"runtime": "python3.9"},
        "estimated_cost": 5.00,
        "status": BuilderConstants.STATES.DRAFT.name
    }

@pytest.fixture
def question_create_data():
    return {
        "difficulty_tier": BuilderConstants.TIERS.T2.name,
        "knowledge_area": "Serverless",
        "personas": [BuilderConstants.PERSONAS.DEV.name],
        "question_text": "What is the maximum timeout for an AWS Lambda function?",
        "question_type": "multiple_choice",
        "options": {
            "a": "15 minutes",
            "b": "5 minutes",
            "c": "30 minutes",
            "d": "1 hour"
        },
        "correct_answer": "a",
        "explanation": "AWS Lambda functions have a maximum timeout of 15 minutes"
    }

@pytest.mark.asyncio
async def test_create_content(session, content_create_data):
    content = LearningContentCreate(**content_create_data)
    db_content = await create_content(session, content)
    
    assert db_content.id is not None
    assert db_content.code_title == content_create_data["code_title"]
    assert db_content.title == content_create_data["title"]
    assert db_content.status == BuilderConstants.STATES.DRAFT.name

@pytest.mark.asyncio
async def test_get_content(session, content_create_data):
    content = LearningContentCreate(**content_create_data)
    created_content = await create_content(session, content)
    
    retrieved_content = await get_content(session, created_content.id)
    
    assert retrieved_content is not None
    assert retrieved_content.id == created_content.id
    assert retrieved_content.code_title == content_create_data["code_title"]

@pytest.mark.asyncio
async def test_get_contents_with_filters(session: AsyncSession, content_create_data):
    content = LearningContentCreate(**content_create_data)
    await create_content(session, content)
    
    filters = {
        "tier": BuilderConstants.TIERS.T2.name,
        "persona": BuilderConstants.PERSONAS.DEV.name
    }
    
    contents = await get_contents(session, filters)
    
    assert len(contents) > 0
    assert contents[0].tier == filters["tier"]
    assert filters["persona"] in contents[0].personas

@pytest.mark.asyncio
async def test_update_content(session: AsyncSession, content_create_data):
    content = LearningContentCreate(**content_create_data)
    created_content = await create_content(session, content)
    
    updates = {
        "status": BuilderConstants.STATES.STAGED.name,
        "notes": "Ready for review"
    }
    
    updated_content = await update_content(session, created_content.id, updates)
    
    assert updated_content.status == BuilderConstants.STATES.STAGED.name
    assert updated_content.notes == "Ready for review"

@pytest.mark.asyncio
async def test_create_assessment_question(session: AsyncSession, question_create_data):
    question = AssessmentQuestionCreate(**question_create_data)
    db_question = await create_assessment_question(session, question)
    
    assert db_question.id is not None
    assert db_question.difficulty_tier == question_create_data["difficulty_tier"]
    assert db_question.question_text == question_create_data["question_text"]

@pytest.mark.asyncio
async def test_get_assessment_questions(session: AsyncSession, question_create_data):
    question = AssessmentQuestionCreate(**question_create_data)
    await create_assessment_question(session, question)
    
    filters = {
        "tier": BuilderConstants.TIERS.T2.name,
        "knowledge_area": "Serverless"
    }
    
    questions = await get_assessment_questions(session, filters)
    
    assert len(questions) > 0
    assert questions[0].difficulty_tier == filters["tier"]
    assert questions[0].knowledge_area == filters["knowledge_area"]

@pytest.mark.asyncio
async def test_create_learning_pathway(session: AsyncSession, content_create_data):
    content = LearningContentCreate(**content_create_data)
    created_content = await create_content(session, content)
    
    pathway_data = {
        "name": "AWS Developer Path",
        "description": "Complete AWS developer learning pathway",
        "target_persona": BuilderConstants.PERSONAS.DEV.name,
        "estimated_duration": 180,
        "total_cost": 15.00,
        "items": [
            PathwayItemCreate(content_id=created_content.id, sequence=1)
        ]
    }
    
    pathway = LearningPathwayCreate(**pathway_data)
    db_pathway = await create_pathway(session, pathway)
    
    assert db_pathway.id is not None
    assert db_pathway.name == pathway_data["name"]
    assert len(db_pathway.items) == 1
    assert db_pathway.items[0].content_id == created_content.id

@pytest.mark.asyncio
async def test_get_pathways(session: AsyncSession, content_create_data):
    content = LearningContentCreate(**content_create_data)
    created_content = await create_content(session, content)
    
    pathway_data = {
        "name": "AWS Developer Path",
        "target_persona": BuilderConstants.PERSONAS.DEV.name,
        "estimated_duration": 180,
        "total_cost": 15.00,
        "items": [
            PathwayItemCreate(content_id=created_content.id, sequence=1)
        ]
    }
    
    pathway = LearningPathwayCreate(**pathway_data)
    await create_pathway(session, pathway)
    
    filters = {
        "target_persona": BuilderConstants.PERSONAS.DEV.name
    }
    
    pathways = await get_pathways(session, filters)
    
    assert len(pathways) > 0
    assert pathways[0].target_persona == filters["target_persona"]
    assert len(pathways[0].items) > 0
