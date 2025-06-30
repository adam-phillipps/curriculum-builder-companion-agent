from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.db.init import initialize_database
from src.api.routes import content, agents

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await initialize_database()
    yield
    # Shutdown (if needed)

app = FastAPI(
    title="Curriculum Builder Companion Agent",
    description="AI-powered curriculum building and analysis platform",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(content.router)
app.include_router(agents.router)