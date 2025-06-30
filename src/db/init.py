from src.db.database import init_db

async def initialize_database():
    """Initialize database tables for production."""
    await init_db()