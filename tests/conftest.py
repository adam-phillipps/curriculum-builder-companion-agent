"""Test configuration and fixtures."""
import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from httpx import AsyncClient

from src.main import app
from src.db.database import Base
from src.config import get_settings

# Test database URL (in-memory SQLite for speed)
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_engine():
    """Create test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=False
    )
    
    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    await engine.dispose()

@pytest.fixture
def test_session_factory(test_engine):
    """Create test database session factory."""
    return async_sessionmaker(test_engine, expire_on_commit=False)

@pytest.fixture
async def test_session(test_session_factory):
    """Create test database session."""
    async with test_session_factory() as session:
        try:
            yield session
        finally:
            await session.rollback()

@pytest.fixture
async def session(test_session_factory):
    """Create database session for tests that expect 'session' fixture."""
    async with test_session_factory() as session:
        try:
            yield session
        finally:
            await session.rollback()

@pytest.fixture
async def client():
    """Create test HTTP client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac

@pytest.fixture
def sample_content():
    """Sample content for testing."""
    return {
        "content": "Learn AWS Lambda basics with Python. This tutorial covers serverless functions, event triggers, and deployment strategies for building scalable cloud applications.",
        "suggested_tier": "T2",
        "suggested_personas": ["developer"],
        "suggested_content_type": "lesson"
    }

@pytest.fixture
def sample_metadata():
    """Sample extracted metadata for testing."""
    return {
        "title": "AWS Lambda Basics",
        "description": "Learn AWS Lambda with Python",
        "tier": "T2",
        "personas": ["developer"],
        "content_type": "lesson",
        "learning_objectives": ["Understand Lambda", "Deploy functions"],
        "estimated_duration": 60,
        "sandbox_type": "individual",
        "aws_services": ["Lambda"],
        "technical_requirements": {"runtime": "python3.9"},
        "estimated_cost": 5.0
    }