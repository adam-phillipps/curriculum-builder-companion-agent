"""
Pathway API routes for learning pathway data and chain rule analysis.
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from src.api.dependencies import get_db
from src.utils.chain_rule import calculate_learning_impact

router = APIRouter(prefix="/pathway", tags=["pathway"])

@router.get("/{pathway_id}/chain-analysis")
async def get_pathway_chain_analysis(
    pathway_id: int,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get chain rule analysis for a learning pathway."""
    
    # Get pathway data from database
    pathway_query = await db.execute(text("""
        SELECT p.id, p.name, p.completion_percentage, p.target_persona
        FROM learning_pathways p 
        WHERE p.id = :pathway_id
    """), {"pathway_id": pathway_id})
    pathway = pathway_query.fetchone()
    
    if not pathway:
        raise HTTPException(status_code=404, detail="Pathway not found")
    
    # Get pathway items with chain rule data
    items_query = await db.execute(text("""
        SELECT pi.content_id, pi.sequence, pi.weight, pi.prerequisite_ids,
               pi.completion_status, pi.completion_percentage, pi.success_score,
               lc.title, lc.description
        FROM pathway_items pi
        JOIN learning_content lc ON pi.content_id = lc.id
        WHERE pi.pathway_id = :pathway_id
        ORDER BY pi.sequence
    """), {"pathway_id": pathway_id})
    items = items_query.fetchall()
    
    # Format data for chain rule calculation
    pathway_data = {
        "pathway": {
            "id": pathway[0],
            "name": pathway[1],
            "completion": pathway[2] or 0.0
        },
        "nodes": []
    }
    
    for item in items:
        try:
            prereqs = eval(item[3]) if item[3] and item[3] != '[]' else []
        except:
            prereqs = []
            
        pathway_data["nodes"].append({
            "id": f"content_{item[0]}",
            "content_id": item[0],
            "sequence": item[1],
            "weight": item[2] or 0.5,
            "prerequisites": prereqs,
            "status": item[4] or "not_started",
            "completion": item[5] or 0.0,
            "success_score": item[6],
            "name": item[7] or f"Content {item[0]}",
            "description": item[8] or ""
        })
    
    # Calculate chain rule impacts
    impact_analysis = calculate_learning_impact(pathway_data)
    
    # Remove non-serializable calculator object
    serializable_analysis = {
        "chain_impacts": {f"{k[0]}->{k[1]}": v for k, v in impact_analysis.get("chain_impacts", {}).items()},
        "node_importance": impact_analysis.get("node_importance", {}),
        "critical_paths": impact_analysis.get("critical_paths", {})
    }
    
    return {
        "pathway_data": pathway_data,
        "chain_analysis": serializable_analysis,
        "total_nodes": len(pathway_data["nodes"])
    }

@router.get("/{user_id}/skill-profile")
async def get_user_skill_profile(
    user_id: int,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Get user skill assessment profile for pathway recommendations."""
    
    skills_query = await db.execute(text("""
        SELECT skill_category, proficiency_level, assessment_date
        FROM user_skill_assessments 
        WHERE user_id = :user_id
        ORDER BY assessment_date DESC
    """), {"user_id": user_id})
    skills = skills_query.fetchall()
    
    skill_profile = {}
    for skill in skills:
        skill_profile[skill[0]] = {
            "proficiency": skill[1],
            "assessed_date": skill[2].isoformat() if skill[2] else None
        }
    
    return {
        "user_id": user_id,
        "skills": skill_profile,
        "total_skills": len(skill_profile)
    }