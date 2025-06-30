from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from src.dependencies import get_postgres_session

# PostgreSQL database dependency
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_postgres_session():
        yield session