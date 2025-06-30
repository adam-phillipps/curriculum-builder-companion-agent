from typing import Dict, List, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
try:
    from langchain_anthropic import ChatAnthropic
except ImportError:
    # Fallback for different versions
    ChatAnthropic = None

from src.db.crud.content import create_content, get_contents
from src.api.schemas.content import LearningContentCreate
from src.config import get_settings, BuilderConstants

settings = get_settings()

def get_llm(provider: str, model: str, temperature: float = 0.7):
    """Get LLM instance based on provider and model."""
    if provider.lower() == "openai":
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=settings.OPENAI_API_KEY.get_secret_value()
        )
    elif provider.lower() == "anthropic":
        if ChatAnthropic is None:
            raise ValueError("Anthropic not available. Install langchain-anthropic")
        return ChatAnthropic(
            model=model,
            temperature=temperature,
            anthropic_api_key=settings.ANTHROPIC_API_KEY.get_secret_value()
        )
    else:
        raise ValueError(f"Unsupported provider: {provider}")

@tool
async def extract_metadata_from_content(
    content: str, 
    suggested_tier: Optional[str] = None,
    suggested_personas: List[str] = [],
    suggested_content_type: Optional[str] = None,
    model_provider: str = "openai",
    model_name: str = "gpt-4"
) -> Dict[str, Any]:
    """Extract structured metadata from learning content."""
    
    llm = get_llm(model_provider, model_name)
    
    # Build context with available options
    tiers = BuilderConstants.TIERS.get_names()
    personas = BuilderConstants.PERSONAS.get_names()
    content_types = BuilderConstants.CONTENT_TYPES.get_names()
    sandbox_types = BuilderConstants.SANDBOX_TYPES.get_names()
    
    prompt = f"""
    Analyze this learning content and extract metadata:
    
    Content: {content}
    
    User suggestions:
    - Tier: {suggested_tier or 'Not specified'}
    - Personas: {suggested_personas or 'Not specified'}
    - Content Type: {suggested_content_type or 'Not specified'}
    
    Available options:
    - Tiers: {tiers}
    - Personas: {personas}
    - Content Types: {content_types}
    - Sandbox Types: {sandbox_types}
    
    Extract and return JSON with:
    - title: Clear, concise title
    - description: 2-3 sentence summary
    - tier: Choose from available tiers (prefer user suggestion if valid)
    - personas: List of relevant personas
    - content_type: Choose from available types
    - learning_objectives: List of 3-5 specific objectives
    - estimated_duration: Minutes to complete
    - sandbox_type: Required sandbox environment
    - aws_services: List of AWS services mentioned
    - technical_requirements: Dict of technical needs
    - estimated_cost: Rough cost estimate in USD
    """
    
    response = await llm.ainvoke(prompt)
    
    # Parse LLM response (simplified for now)
    # In production, use structured output or JSON parsing
    return {
        "title": "Extracted Title",
        "description": "Extracted description",
        "tier": suggested_tier or "T2",
        "personas": suggested_personas or ["developer"],
        "content_type": suggested_content_type or "lesson",
        "learning_objectives": ["Learn basics", "Apply concepts"],
        "estimated_duration": 60,
        "sandbox_type": "individual",
        "aws_services": ["Lambda"],
        "technical_requirements": {"runtime": "python3.9"},
        "estimated_cost": 5.0
    }

async def _search_similar_content(
    metadata: Dict[str, Any],
    db_session: AsyncSession,
    threshold: float = 0.85
) -> List[Dict[str, Any]]:
    """Internal function to search for similar content in database."""
    
    # Simple metadata-based similarity for now
    filters = {
        "tier": metadata.get("tier"),
        "content_type": metadata.get("content_type")
    }
    
    similar_items = await get_contents(db_session, filters, limit=5)
    
    return [
        {
            "id": item.id,
            "title": item.title,
            "similarity_score": 0.7,  # Placeholder
            "tier": item.tier,
            "content_type": item.content_type
        }
        for item in similar_items
    ]

async def _create_learning_content(
    metadata: Dict[str, Any],
    raw_content: str,
    db_session: AsyncSession,
    user_id: Optional[str] = None
) -> int:
    """Internal function to create learning content in database."""
    
    # Generate unique code_title
    import random
    code_title = f"{metadata['tier']}.{metadata['personas'][0][:3].upper()}.{random.randint(100, 999):03d}"
    
    content_data = LearningContentCreate(
        code_title=code_title,
        title=metadata["title"],
        description=metadata["description"],
        content_type=metadata["content_type"],
        tier=metadata["tier"],
        personas=metadata["personas"],
        learning_objectives=metadata["learning_objectives"],
        estimated_duration=metadata["estimated_duration"],
        sandbox_type=metadata["sandbox_type"],
        aws_services=metadata.get("aws_services", []),
        technical_requirements=metadata.get("technical_requirements", {}),
        estimated_cost=metadata["estimated_cost"],
        status="draft"
    )
    
    db_content = await create_content(db_session, content_data)
    return db_content.id

def create_content_tools(db_session: AsyncSession):
    """Create tools with database session bound - Tool Factory Pattern."""
    
    @tool
    async def search_similar_content(
        metadata: Dict[str, Any],
        threshold: float = 0.85
    ) -> List[Dict[str, Any]]:
        """Search for similar content in database."""
        return await _search_similar_content(metadata, db_session, threshold)
    
    @tool
    async def create_learning_content(
        metadata: Dict[str, Any],
        raw_content: str,
        user_id: Optional[str] = None
    ) -> int:
        """Create learning content in database."""
        return await _create_learning_content(metadata, raw_content, db_session, user_id)
    
    return [search_similar_content, create_learning_content]