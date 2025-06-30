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
    You are an expert curriculum designer. Analyze this learning content and extract structured metadata.
    
    CONTENT TO ANALYZE:
    {content}
    
    USER SUGGESTIONS:
    - Tier: {suggested_tier or 'Not specified'}
    - Personas: {suggested_personas or 'Not specified'}
    - Content Type: {suggested_content_type or 'Not specified'}
    
    AVAILABLE OPTIONS:
    - Tiers: {tiers} (T1=Foundational, T2=Intermediate, T3=Advanced, T4=Expert)
    - Personas: {personas}
    - Content Types: {content_types}
    - Sandbox Types: {sandbox_types}
    
    RESPOND WITH VALID JSON ONLY:
    {{
        "title": "Clear, concise title (max 60 chars)",
        "description": "2-3 sentence summary describing what learners will do",
        "tier": "Choose from {tiers} - prefer user suggestion if valid",
        "personas": ["List of 1-3 most relevant personas from {personas}"],
        "content_type": "Choose from {content_types}",
        "learning_objectives": ["3-5 specific, measurable learning objectives"],
        "estimated_duration": 60,
        "sandbox_type": "Choose from {sandbox_types}",
        "aws_services": ["List AWS services mentioned in content"],
        "technical_requirements": {{"runtime": "python3.9", "other": "requirements"}},
        "estimated_cost": 5.0
    }}
    
    Return ONLY the JSON object, no other text.
    """
    
    # For now, skip LLM and return fallback metadata to test the workflow
    print(f"DEBUG: Skipping LLM call, using fallback metadata")
    
    # Return fallback metadata based on content analysis
    return _extract_from_text(content, suggested_tier, suggested_personas, suggested_content_type)
    
    # TODO: Re-enable LLM extraction once we have proper API keys and error handling
    # try:
    #     response = await llm.ainvoke(prompt)
    #     # ... LLM processing code ...
    # except Exception as e:
    #     print(f"LLM extraction error: {e}")
    #     return fallback_metadata

async def _search_similar_content(
    metadata: Dict[str, Any],
    db_session: AsyncSession,
    threshold: float = 0.3,
    query_text: str = ""
) -> List[Dict[str, Any]]:
    """Internal function to search for similar content using vector store."""
    
    from src.services.vector_store import vector_store
    
    print(f"DEBUG: Vector searching with metadata: {metadata}")
    
    try:
        # Create search query from metadata
        search_query = query_text or f"{metadata.get('title', '')} {metadata.get('description', '')}"
        
        # Prepare metadata filters for ChromaDB
        filters = {}
        if metadata.get("tier"):
            filters["tier"] = metadata["tier"]
        if metadata.get("content_type"):
            filters["content_type"] = metadata["content_type"]
        if metadata.get("estimated_duration"):
            filters["estimated_duration"] = metadata["estimated_duration"]
        
        # Search vector store (search both approved and draft content)
        similar_items = vector_store.find_similar_content(
            query_text=search_query,
            metadata_filters=filters,
            similarity_threshold=threshold,
            max_results=5,
            search_approved_only=False
        )
        
        print(f"DEBUG: Vector search found {len(similar_items)} similar items")
        return similar_items
        
    except Exception as e:
        print(f"DEBUG: Error in vector similarity search: {e}")
        import traceback
        traceback.print_exc()
        
        # Fallback to database search
        print("DEBUG: Falling back to database search")
        filters = {
            "tier": metadata.get("tier"),
            "content_type": metadata.get("content_type")
        }
        
        similar_items = await get_contents(db_session, filters, limit=5)
        
        return [
            {
                "content_id": item.id,
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
    """Internal function to create learning content in database and vector store."""
    
    from src.services.vector_store import vector_store
    
    # Generate unique code_title
    import random
    personas = metadata.get('personas', ['DEV'])  # Default fallback
    code_title = f"{metadata['tier']}.{personas[0][:3].upper()}.{random.randint(100, 999):03d}"
    
    content_data = LearningContentCreate(
        code_title=code_title,
        title=metadata.get("title", "Learning Content"),
        description=metadata.get("description", "Generated learning content"),
        content_type=metadata.get("content_type", "lesson"),
        tier=metadata.get("tier", "T2"),
        personas=metadata.get("personas", ["developer"]),
        learning_objectives=metadata.get("learning_objectives", ["Learn concepts"]),
        estimated_duration=metadata.get("estimated_duration", 30),
        sandbox_type=metadata.get("sandbox_type", "individual"),
        aws_services=metadata.get("aws_services", []),
        technical_requirements=metadata.get("technical_requirements", {}),
        estimated_cost=metadata.get("estimated_cost", 5.0),
        status="draft"
    )
    
    # Create in database
    db_content = await create_content(db_session, content_data)
    
    # Add to vector store (draft collection)
    try:
        vector_id = vector_store.add_content(
            content_id=db_content.id,
            title=metadata.get("title", "Learning Content"),
            description=metadata.get("description", "Generated learning content"),
            content_text=raw_content,
            metadata=metadata,
            is_approved=False  # Draft content
        )
        print(f"DEBUG: Added content to vector store with ID: {vector_id}")
    except Exception as e:
        print(f"DEBUG: Error adding to vector store: {e}")
        import traceback
        traceback.print_exc()
        # Continue without vector store - not critical for MVP
    
    return db_content.id

def _extract_from_text(text: str, suggested_tier: str, suggested_personas: List[str], suggested_content_type: str) -> Dict[str, Any]:
    """Extract metadata from plain text response as fallback."""
    # Simple text analysis fallback
    aws_services = []
    if "lambda" in text.lower():
        aws_services.append("Lambda")
    if "s3" in text.lower():
        aws_services.append("S3")
    if "ec2" in text.lower():
        aws_services.append("EC2")
    
    # Estimate duration based on content length
    word_count = len(text.split())
    estimated_duration = max(30, min(180, word_count // 5))  # 30-180 minutes, ~5 words per minute reading
    
    return {
        "title": "Learning Content",
        "description": text[:200] + "..." if len(text) > 200 else text,
        "tier": suggested_tier or "T2",
        "personas": suggested_personas or ["developer"],
        "content_type": suggested_content_type or "lesson",
        "learning_objectives": ["Understand core concepts", "Apply practical skills"],
        "estimated_duration": estimated_duration,
        "sandbox_type": "individual",
        "aws_services": aws_services,
        "technical_requirements": {"runtime": "python3.9"},
        "estimated_cost": 5.0
    }

def create_content_tools(db_session: AsyncSession):
    """Create tools with database session bound - Tool Factory Pattern."""
    
    @tool
    async def search_similar_content(
        metadata: Dict[str, Any],
        threshold: float = 0.3,
        query_text: str = ""
    ) -> List[Dict[str, Any]]:
        """Search for similar content using vector store."""
        return await _search_similar_content(metadata, db_session, threshold, query_text)
    
    @tool
    async def create_learning_content(
        metadata: Dict[str, Any],
        raw_content: str,
        user_id: Optional[str] = None
    ) -> int:
        """Create learning content in database."""
        return await _create_learning_content(metadata, raw_content, db_session, user_id)
    
    return [search_similar_content, create_learning_content]