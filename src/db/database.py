from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import async_sessionmaker
from src.config import get_settings

settings = get_settings()

# Create declarative base
Base = declarative_base()

# Import models for metadata registration
from src.db.models.content import *
from src.db.models.pricing import *
from src.db.models.topic import *
from src.db.models.user import *

# Create async engine
engine = create_async_engine(
    str(settings.DATABASE_URL).replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.DEBUG,
)

# Create async session maker
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def init_db():
    """Initialize the database."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)