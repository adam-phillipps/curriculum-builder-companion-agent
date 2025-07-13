"""
Pathway API routes for learning pathway data and chain rule analysis.
"""
from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text

from src.api.dependencies import get_db
from src.utils.chain_rule import calculate_learning_impact
from src.db.crud.user import get_user_content_progress

def calculate_domain_similarity(node1: dict, node2: dict) -> float:
    """Calculate similarity between two nodes based on domain tags."""
    tags1 = set(node1.get("domain_tags", []))
    tags2 = set(node2.get("domain_tags", []))
    
    if not tags1 or not tags2:
        return 0.1  # Minimal similarity for untagged content
    
    # Exact domain match
    intersection = tags1.intersection(tags2)
    if intersection:
        return 1.0
    
    # Domain similarity mapping (simplified)
    domain_groups = {
        "ml_engineer": ["architect", "developer", "data_science"],
        "architect": ["ml_engineer", "developer"],
        "developer": ["ml_engineer", "architect"],
        "law": ["politics", "research"],
        "politics": ["law", "research"],
        "research": ["law", "politics", "data_science"],
        "data_science": ["ml_engineer", "research"]
    }
    
    # Check for related domains
    for tag1 in tags1:
        for tag2 in tags2:
            if tag1 in domain_groups and tag2 in domain_groups.get(tag1, []):
                return 0.6  # Related domain
    
    return 0.2  # Distant domains

router = APIRouter(prefix="/pathway", tags=["pathway"])

@router.get("/user-pathway/{user_id}")
async def generate_user_pathway(
    user_id: int,
    root_content_id: int = 0,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """Generate pathway data for user's enrolled content."""
    # Force reload
    
    try:
        # Get progress records using the same approach as users API
        print(f"DEBUG: Getting progress for user {user_id}")
        progress_records = await get_user_content_progress(db, user_id)
        print(f"DEBUG: Got {len(progress_records) if progress_records else 0} records")
        
        if not progress_records:
            return {
                "user_id": user_id,
                "root_node_id": None,
                "domain_focus": "Learning Pathway",
                "pathway_strength": 0.0,
                "total_estimated_hours": 0,
                "nodes": [],
                "edges": []
            }
        
        # Convert to pathway nodes
        nodes = []
        for progress in progress_records:
            content = progress.content
            
            # Extract basic info
            domain_tags = [content.tier]
            if content.personas:
                domain_tags.append(content.personas[0])
            
            # Calculate vertical distance (tier-based)
            tier_values = {'T1': 1, 'T2': 2, 'T3': 3, 'T4': 4}
            vertical_distance = tier_values.get(content.tier, 2)
            
            node = {
                "id": f"node_{content.id}",
                "content_id": content.id,
                "title": content.title,
                "description": content.description,
                "tier": content.tier,
                "status": progress.status,
                "progress_percentage": progress.progress_percentage,
                "comprehension_percentage": progress.comprehension_percentage or 0.0,
                "prerequisites": [],  # Skip for now to avoid async issues
                "learning_outcomes": content.learning_objectives or [],
                "domain_tags": domain_tags,
                "weight": 0.5,
                "horizontal_distance": 0.5,
                "vertical_distance": vertical_distance
            }
            nodes.append(node)
        
        # Get user's primary learning outcome as root node
        from src.db.crud.user import get_learner_profile
        from src.db.models.learning_outcomes import LearningOutcome
        
        learner_profile = await get_learner_profile(db, user_id)
        root_learning_outcome = None
        
        if learner_profile and learner_profile.primary_learning_outcome_id:
            result = await db.execute(
                select(LearningOutcome)
                .where(LearningOutcome.id == learner_profile.primary_learning_outcome_id)
            )
            outcome = result.scalar_one_or_none()
            
            if outcome:
                root_learning_outcome = {
                    "id": f"outcome_{outcome.id}",
                    "content_id": outcome.id,
                    "title": outcome.name,
                    "description": outcome.description,
                    "tier": "ROOT",
                    "status": "target",
                    "progress_percentage": 0,
                    "comprehension_percentage": 0,
                    "prerequisites": [],
                    "learning_outcomes": [outcome.name],
                    "domain_tags": [outcome.domain or "general"],
                    "weight": 1.0,
                    "horizontal_distance": 0.0,
                    "vertical_distance": 10  # Highest level
                }
                nodes.append(root_learning_outcome)
        
        # Generate edges with proper domain similarity and progression
        edges = []
        
        # Sort nodes by difficulty (vertical distance)
        sorted_nodes = sorted(nodes, key=lambda n: n["vertical_distance"])
        
        for i, node in enumerate(sorted_nodes):
            # Skip if this is the root outcome
            if node.get("tier") == "ROOT":
                continue
                
            # Find next progression target
            target_node = None
            best_score = 0
            
            # Look for higher difficulty nodes
            for candidate in sorted_nodes[i+1:]:
                # Calculate similarity score
                domain_similarity = calculate_domain_similarity(node, candidate)
                difficulty_progression = candidate["vertical_distance"] - node["vertical_distance"]
                
                # Prefer same domain with next difficulty level
                score = domain_similarity * 0.7 + (1.0 / max(difficulty_progression, 1)) * 0.3
                
                if score > best_score and score > 0.3:  # Minimum threshold
                    best_score = score
                    target_node = candidate
            
            # Create edge if target found
            if target_node:
                edges.append({
                    "source_id": node["id"],
                    "target_id": target_node["id"],
                    "relationship_type": "progression" if best_score > 0.7 else "bridge",
                    "strength": best_score
                })
            # If no progression found, connect to root if it exists
            elif root_learning_outcome:
                edges.append({
                    "source_id": node["id"],
                    "target_id": root_learning_outcome["id"],
                    "relationship_type": "aspiration",
                    "strength": 0.3
                })
        
        # Determine root node
        root_node_id = None
        if root_content_id > 0:
            # User clicked on specific content as temporary root
            root_node_id = f"node_{root_content_id}"
        elif root_learning_outcome:
            # Use primary learning outcome as root
            root_node_id = root_learning_outcome["id"]
        else:
            # Fallback to highest difficulty node
            if nodes:
                highest_tier_node = max(nodes, key=lambda n: n["vertical_distance"])
                root_node_id = highest_tier_node["id"]
        
        return {
            "user_id": user_id,
            "root_node_id": root_node_id,
            "domain_focus": "Learning Pathway",
            "pathway_strength": 0.7,
            "total_estimated_hours": sum(n["vertical_distance"] * 15 for n in nodes),
            "nodes": nodes,
            "edges": edges
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate pathway: {str(e)}")

@router.get("/skill-profile/{user_id}")
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