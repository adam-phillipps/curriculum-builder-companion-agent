from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from src.db.init import initialize_database
from src.api.routes import content, agents, vector_store, analysis, users, pathway, progress, learning_outcomes

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    # await initialize_database()  # Temporarily disabled
    yield
    # Shutdown (if needed)

app = FastAPI(
    title="Curriculum Builder Companion Agent",
    description="AI-powered curriculum building and analysis platform",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(content.router)
app.include_router(agents.router)
app.include_router(vector_store.router)
app.include_router(analysis.router)
app.include_router(users.router)
app.include_router(pathway.router)
app.include_router(progress.router)
app.include_router(learning_outcomes.router)

# Serve documentation if built
docs_path = os.path.join(os.path.dirname(__file__), "..", "site")
if os.path.exists(docs_path):
    app.mount("/docs", StaticFiles(directory=docs_path, html=True), name="docs")

@app.get("/health")
async def health_check():
    """Application health check."""
    return {"status": "healthy", "service": "curriculum-builder"}