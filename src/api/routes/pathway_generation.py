"""
API routes for dynamic pathway generation.
"""
from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db
from src.services.pathway_generator import pathway_generator

router = APIRouter(prefix="/pathway-generation", tags=["pathway-generation"])

@router.get("/user/{user_id}")
async def generate_user_pathway(
    user_id: int,
    root_content_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Generate a learning pathway for user's enrolled content."""
    
    try:
        pathway = await pathway_generator.generate_user_pathway(
            db=db,
            user_id=user_id,
            root_content_id=root_content_id
        )
        
        # Convert to JSON-serializable format
        return {
            "user_id": pathway.user_id,
            "root_node_id": pathway.root_node_id,
            "domain_focus": pathway.domain_focus,
            "pathway_strength": pathway.pathway_strength,
            "total_estimated_hours": pathway.total_estimated_hours,
            "nodes": [
                {
                    "id": node.id,
                    "content_id": node.content_id,
                    "title": node.title,
                    "description": node.description,
                    "tier": node.tier,
                    "status": node.status,
                    "progress_percentage": node.progress_percentage,
                    "comprehension_percentage": node.comprehension_percentage,
                    "prerequisites": node.prerequisites,
                    "learning_outcomes": node.learning_outcomes,
                    "domain_tags": node.domain_tags,
                    "weight": node.weight,
                    "horizontal_distance": node.horizontal_distance,
                    "vertical_distance": node.vertical_distance
                }
                for node in pathway.nodes
            ],
            "edges": [
                {
                    "source_id": edge.source_id,
                    "target_id": edge.target_id,
                    "relationship_type": edge.relationship_type,
                    "strength": edge.strength
                }
                for edge in pathway.edges
            ]
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate pathway: {str(e)}")

@router.get("/user/{user_id}/root/{root_content_id}")
async def generate_pathway_with_root(
    user_id: int,
    root_content_id: int,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Generate pathway with specific root node (for when user clicks on a node)."""
    
    return await generate_user_pathway(user_id, root_content_id, db)