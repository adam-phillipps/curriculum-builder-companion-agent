from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from src.config import settings
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
    description="AI-powered curriculum building and analysis platform for educators",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_tags=[
        {"name": "system", "description": "System health and information"},
        {"name": "content", "description": "Learning content management"},
        {"name": "agents", "description": "AI-powered content processing"},
        {"name": "learning-outcomes", "description": "Learning goals and objectives"},
        {"name": "progress", "description": "Progress tracking and analytics"},
        {"name": "users", "description": "User management and profiles"},
        {"name": "pathways", "description": "Learning pathway management"},
        {"name": "vector-store", "description": "Similarity search and recommendations"},
        {"name": "analysis", "description": "Gap analysis and insights"}
    ]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000", 
        "http://frontend:3000",
        "https://dczs8zbwc9iyf.cloudfront.net",
        "*"  # Allow all origins for now - should be restricted in production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(content.router, prefix="/api/v1")
app.include_router(agents.router, prefix="/api/v1")
app.include_router(vector_store.router, prefix="/api/v1")
app.include_router(analysis.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(pathway.router, prefix="/api/v1")
app.include_router(progress.router, prefix="/api/v1")
app.include_router(learning_outcomes.router, prefix="/api/v1")

# Documentation service link
@app.get("/docs", tags=["system"])
async def docs_redirect():
    """Redirect to documentation service.
    
    Returns:
        dict: Documentation service information and links
    """
    docs_url = f"http://{settings.DOCS_HOST}:{settings.DOCS_PORT}"
    return {
        "message": "Documentation Service",
        "product_docs": docs_url,
        "api_docs": "/api/docs",
        "instructions": "Run 'docker compose --profile docs up -d' to start documentation service"
    }

@app.get("/health", tags=["system"])
async def health_check():
    """Application health check endpoint.
    
    Returns:
        dict: Health status and service information
    """
    return {"status": "healthy", "service": "curriculum-builder", "version": "1.0.0"}

@app.get("/", tags=["system"])
async def root():
    """API root endpoint with navigation links.
    
    Returns:
        dict: API information and documentation links
    """
    docs_url = f"http://{settings.DOCS_HOST}:{settings.DOCS_PORT}"
    return {
        "message": "Curriculum Builder Companion Agent API",
        "version": "1.0.0",
        "api_docs": "/api/docs",
        "api_docs_redoc": "/api/redoc",
        "product_docs": docs_url,
        "health_check": "/health"
    }