from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import async_session_maker

async def get_postgres_session() -> AsyncGenerator[AsyncSession, None]:
    """Get PostgreSQL database session."""
    async with async_session_maker() as session:
        yield session