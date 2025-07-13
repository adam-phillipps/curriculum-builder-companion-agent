"""
Vector store API endpoints for content similarity and search.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from src.services.vector_store import vector_store

router = APIRouter(prefix="/vector", tags=["vector-store"])

class SimilaritySearchRequest(BaseModel):
    """Request model for similarity search."""
    query_text: str
    metadata_filters: Optional[Dict[str, Any]] = None
    similarity_threshold: float = 0.3
    max_results: int = 10
    search_approved_only: bool = False
    
class MetadataFilters(BaseModel):
    """Enhanced metadata filters for search."""
    tier: Optional[str] = None
    content_type: Optional[str] = None
    sandbox_type: Optional[str] = None
    author: Optional[str] = None
    personas: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    aws_services: Optional[List[str]] = None
    duration_min: Optional[int] = None
    duration_max: Optional[int] = None
    cost_min: Optional[float] = None
    cost_max: Optional[float] = None
    created_after: Optional[str] = None
    created_before: Optional[str] = None
    updated_after: Optional[str] = None
    updated_before: Optional[str] = None
    is_approved: Optional[bool] = None

class SimilaritySearchResponse(BaseModel):
    """Response model for similarity search."""
    results: List[Dict[str, Any]]
    total_found: int
    search_time_ms: Optional[float] = None

@router.post("/search", response_model=SimilaritySearchResponse)
async def search_similar_content(request: SimilaritySearchRequest):
    """Search for similar content using vector similarity with enhanced metadata filtering."""
    try:
        import time
        start_time = time.time()
        
        results = vector_store.find_similar_content(
            query_text=request.query_text,
            metadata_filters=request.metadata_filters,
            similarity_threshold=request.similarity_threshold,
            max_results=request.max_results,
            search_approved_only=request.search_approved_only
        )
        
        search_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        return SimilaritySearchResponse(
            results=results,
            total_found=len(results),
            search_time_ms=round(search_time, 2)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/metadata/schema")
async def get_metadata_schema():
    """Get the metadata schema for filtering."""
    from src.vector_store.metadata_mapper import metadata_mapper
    
    return {
        "searchable_fields": metadata_mapper.get_searchable_fields(),
        "array_fields": metadata_mapper.get_array_fields(),
        "schema": {
            field_name: {
                "type": field_def.type.value,
                "required": field_def.required,
                "description": field_def.description
            }
            for field_name, field_def in metadata_mapper.METADATA_SCHEMA.items()
        }
    }

@router.get("/stats")
async def get_vector_store_stats():
    """Get vector store statistics."""
    try:
        stats = vector_store.get_content_stats()
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@router.get("/health")
async def vector_store_health():
    """Check vector store health."""
    try:
        stats = vector_store.get_content_stats()
        if "error" in stats:
            raise HTTPException(status_code=503, detail="Vector store unhealthy")
        
        return {
            "status": "healthy",
            "collections": {
                "approved": stats.get("approved_content_count", 0),
                "draft": stats.get("draft_content_count", 0)
            }
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Vector store unhealthy: {str(e)}")

@router.get("/debug")
async def debug_vector_store():
    """Debug endpoint to check vector store contents."""
    try:
        from src.vector_store.metadata_mapper import metadata_mapper
        
        stats = vector_store.get_content_stats()
        
        # Try a simple search to test functionality
        test_results = vector_store.find_similar_content(
            query_text="AWS Lambda tutorial",
            similarity_threshold=0.1,
            max_results=5,
            search_approved_only=False
        )
        
        return {
            "stats": stats,
            "test_search_results": len(test_results),
            "sample_results": test_results[:2] if test_results else [],
            "metadata_schema": {
                "total_fields": len(metadata_mapper.METADATA_SCHEMA),
                "searchable_fields": metadata_mapper.get_searchable_fields(),
                "array_fields": metadata_mapper.get_array_fields()
            }
        }
    except Exception as e:
        return {"error": str(e)}