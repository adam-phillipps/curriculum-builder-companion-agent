from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from src.config import settings
from src.db.init import initialize_database
from src.api.routes import content, agents, vector_store, analysis, users, pathway, progress, learning_outcomes
from src.api.middleware import setup_middleware
from src.utils.logger import get_logger

# Create application logger
logger = get_logger("app")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info(f"Starting application in {settings.APP_ENV} environment")
    # await initialize_database()  # Temporarily disabled
    yield
    # Shutdown (if needed)
    logger.info("Shutting down application")

app = FastAPI(
    title="Curriculum Builder Companion Agent",
    description="AI-powered curriculum building and analysis platform for educators",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    redirect_slashes=False,  # Disable automatic redirects for trailing slashes
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

# Production-grade CORS validation function
def validate_cors_origin(origin: str) -> bool:
    """Validate CORS origin against allowed patterns."""
    if settings.APP_ENV == "development" and settings.CORS_ALLOW_ALL_DEV:
        return True
    
    # Parse origin to get host
    try:
        from urllib.parse import urlparse
        parsed = urlparse(origin)
        host = parsed.netloc or parsed.path
    except:
        return False
    
    # Check against allowed host patterns
    for pattern in settings.CORS_ALLOWED_HOSTS:
        if pattern.startswith("*."):
            # Wildcard subdomain matching
            domain_suffix = pattern[2:]
            if host.endswith(f".{domain_suffix}") or host == domain_suffix:
                return True
        elif host == pattern:
            # Exact match
            return True
    
    return False

# Configure CORS with pattern-based validation
if settings.APP_ENV == "development" and settings.CORS_ALLOW_ALL_DEV:
    # Development: allow all
    cors_origins = ["*"]
    cors_credentials = False
else:
    # Production: use regex pattern for CloudFront and AWS domains
    cors_origins = None
    cors_credentials = True

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_origin_regex=r"https://.*\.cloudfront\.net|https://.*\.amazonaws\.com|http://localhost:3000|https://localhost:3000|http://frontend:3000" if not cors_origins else None,
    allow_credentials=cors_credentials,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Setup middleware
setup_middleware(app)

# Include routers
app.include_router(content.router, prefix="/api/v1")
app.include_router(agents.router, prefix="/api/v1")
app.include_router(vector_store.router, prefix="/api/v1")
app.include_router(analysis.router, prefix="/api/v1")
app.include_router(users.router, prefix="/api/v1")
app.include_router(pathway.router, prefix="/api/v1")
app.include_router(progress.router, prefix="/api/v1")
app.include_router(learning_outcomes.router, prefix="/api/v1")

logger.info("All routes registered successfully")

# Mount documentation as static files
if os.path.exists("/app/docs/site"):
    app.mount("/api/v1/docs", StaticFiles(directory="/app/docs/site", html=True), name="docs")
else:
    # Fallback if docs not built
    @app.get("/api/v1/docs", tags=["system"])
    @app.get("/api/v1/docs/", tags=["system"])
    async def docs_fallback():
        """Documentation not available."""
        return {
            "message": "Documentation not built",
            "api_docs": "/api/docs",
            "instructions": "Documentation needs to be built during container build process"
        }

@app.get("/health", tags=["system"])
async def health_check():
    """Application health check endpoint.
    
    Returns:
        dict: Health status and service information
    """
    logger.debug("Health check requested")
    return {"status": "healthy", "service": "curriculum-builder", "version": "1.0.0"}

@app.get("/", tags=["system"])
async def root():
    """API root endpoint with navigation links.
    
    Returns:
        dict: API information and documentation links
    """
    return {
        "message": "Curriculum Builder Companion Agent API",
        "version": "1.0.0",
        "api_docs": "/api/docs",
        "api_docs_redoc": "/api/redoc",
        "product_docs": "/docs",
        "health_check": "/health"
    }