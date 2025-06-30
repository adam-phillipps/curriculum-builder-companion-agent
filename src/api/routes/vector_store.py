"""
Vector store API endpoints for content similarity and search.
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

from src.services.vector_store import vector_store

router = APIRouter(prefix="/api/v1/vector", tags=["vector-store"])

class SimilaritySearchRequest(BaseModel):
    """Request model for similarity search."""
    query_text: str
    metadata_filters: Optional[Dict[str, Any]] = None
    similarity_threshold: float = 0.8
    max_results: int = 10
    search_approved_only: bool = True

class SimilaritySearchResponse(BaseModel):
    """Response model for similarity search."""
    results: List[Dict[str, Any]]
    total_found: int
    search_time_ms: Optional[float] = None

@router.post("/search", response_model=SimilaritySearchResponse)
async def search_similar_content(request: SimilaritySearchRequest):
    """Search for similar content using vector similarity."""
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