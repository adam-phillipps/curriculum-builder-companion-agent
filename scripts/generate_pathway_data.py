#!/usr/bin/env python3
"""
Generate mock pathway data for testing.
Supports both simple linear pathways and complex multi-branch Sankey pathways.
"""
import asyncio
import sys
import os
from sqlalchemy import text
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db.database import async_session_maker

async def generate_simple_pathway(user_id: int, db):
    """Generate simple linear pathway (original version)."""
    print(f"generating simple data for {user_id}")
    pathway_data = {
        "user_id": user_id,
        "name": "Basic Learning Path",
        "description": "Simple linear learning progression",
        "target_persona": "developer",
        "estimated_duration": 60,
        "total_cost": 0.0
    }
    
    await db.execute(text(
        "INSERT INTO learning_pathways (user_id, name, description, target_persona, estimated_duration, total_cost) "
        "VALUES (:user_id, :name, :description, :target_persona, :estimated_duration, :total_cost)"
    ), pathway_data)
    
    result = await db.execute(text("SELECT id FROM learning_pathways WHERE user_id = :user_id ORDER BY id DESC LIMIT 1"), {"user_id": user_id})
    pathway_id = result.fetchone()[0]
    
    # Simple linear progression
    pathway_items = [
        {"pathway_id": pathway_id, "content_id": 1, "sequence": 1, "weight": 0.6, "prereqs": "[]", "status": "completed", "progress": 90, "time": 180, "score": 0.9},
        {"pathway_id": pathway_id, "content_id": 2, "sequence": 2, "weight": 0.8, "prereqs": "[1]", "status": "completed", "progress": 75, "time": 240, "score": 0.75},
        {"pathway_id": pathway_id, "content_id": 3, "sequence": 3, "weight": 0.7, "prereqs": "[2]", "status": "in_progress", "progress": 40, "time": 120, "score": 0.4},
        {"pathway_id": pathway_id, "content_id": 4, "sequence": 4, "weight": 0.9, "prereqs": "[3]", "status": "not_started", "progress": 0, "time": 0, "score": None}
    ]
    
    return pathway_id, pathway_items, "Simple Linear Pathway"

async def generate_complex_pathway(user_id: int, db):
    """Generate complex multi-branch Sankey pathway with proper learning objectives."""
    print(f"generating complex data for {user_id}")
    pathway_data = {
        "user_id": user_id,
        "name": "Neural Networks Mastery",
        "description": "Complete pathway from math foundations to building neural networks from scratch",
        "target_persona": "ml_engineer",
        "estimated_duration": 120,
        "total_cost": 0.0
    }
    
    await db.execute(text(
        "INSERT INTO learning_pathways (user_id, name, description, target_persona, estimated_duration, total_cost) "
        "VALUES (:user_id, :name, :description, :target_persona, :estimated_duration, :total_cost)"
    ), pathway_data)
    
    result = await db.execute(text("SELECT id FROM learning_pathways WHERE user_id = :user_id ORDER BY id DESC LIMIT 1"), {"user_id": user_id})
    pathway_id = result.fetchone()[0]
    
    # Create learning content with all required fields
    learning_content = [
        {"id": 101, "title": "Basic Math", "objectives": ["Mathematics Fundamentals"], "prereqs": []},
        {"id": 102, "title": "Linear Algebra", "objectives": ["Mathematics Fundamentals"], "prereqs": [101]},
        {"id": 103, "title": "Python Basics", "objectives": ["Programming Fundamentals"], "prereqs": []},
        {"id": 104, "title": "Data Structures", "objectives": ["Programming Fundamentals"], "prereqs": [103]},
        {"id": 105, "title": "Machine Learning Theory", "objectives": ["ML Theory"], "prereqs": [102, 104]},
        {"id": 106, "title": "Neural Networks", "objectives": ["Neural Networks Mastery"], "prereqs": [105]}
    ]
    
    # Check if content exists first, then create if needed
    import json
    for content in learning_content:
        # Check if content exists
        existing = await db.execute(text("SELECT id FROM learning_content WHERE id = :id"), {"id": content["id"]})
        if existing.fetchone():
            print(f"Content {content['id']} already exists, skipping")
            continue
            
        # Create new content with all required fields
        await db.execute(text(
            "INSERT INTO learning_content (id, code_title, title, description, content_type, tier, personas, learning_objectives, estimated_duration, sandbox_type, estimated_cost, status) "
            "VALUES (:id, :code_title, :title, :description, 'lesson', 'T2', :personas, :objectives, 60, 'individual', 5.0, 'draft')"
        ), {
            "id": content["id"],
            "code_title": f"T2.ML.{content['id']}",
            "title": content["title"],
            "description": f"Learn {content['title']} concepts for neural networks pathway",
            "objectives": json.dumps(content["objectives"]),
            "personas": json.dumps(["ml_engineer"])
        })
    
    # Tree structure: leaves → intermediate → root
    pathway_items = [
        {"pathway_id": pathway_id, "content_id": 101, "sequence": 1, "weight": 0.6, "prereqs": "[]", "status": "completed", "progress": 100, "time": 120, "score": 1.0},
        {"pathway_id": pathway_id, "content_id": 102, "sequence": 2, "weight": 0.8, "prereqs": "[101]", "status": "completed", "progress": 85, "time": 180, "score": 0.85},
        {"pathway_id": pathway_id, "content_id": 103, "sequence": 3, "weight": 0.7, "prereqs": "[]", "status": "completed", "progress": 90, "time": 150, "score": 0.9},
        {"pathway_id": pathway_id, "content_id": 104, "sequence": 4, "weight": 0.9, "prereqs": "[103]", "status": "in_progress", "progress": 60, "time": 100, "score": 0.6},
        {"pathway_id": pathway_id, "content_id": 105, "sequence": 5, "weight": 0.7, "prereqs": "[102,104]", "status": "in_progress", "progress": 40, "time": 80, "score": 0.4},
        {"pathway_id": pathway_id, "content_id": 106, "sequence": 6, "weight": 1.0, "prereqs": "[105]", "status": "not_started", "progress": 0, "time": 0, "score": None}
    ]
    
    return pathway_id, pathway_items, "Complex Multi-Branch Sankey Pathway"

async def generate_pathway_data(pathway_type: str = "simple"):
    """Generate pathway data based on type selection."""
    async with async_session_maker() as db:
        # Get first user (John Doe)
        result = await db.execute(text("SELECT id, first_name, last_name, email FROM users ORDER BY id LIMIT 1"))
        user_row = result.fetchone()
        
        if not user_row:
            print("No users found. Create a user first.")
            return
            
        user_id, first_name, last_name, email = user_row
        print(f"\n🎯 Generating {pathway_type} pathway data for:")
        print(f"   User ID: {user_id}")
        print(f"   Name: {first_name} {last_name}")
        print(f"   Email: {email}")
        print(f"   Pathway Type: {pathway_type.upper()}\n")
        
        # Generate pathway based on type
        if pathway_type.lower() == "complex":
            pathway_id, pathway_items, description = await generate_complex_pathway(user_id, db)
        else:
            pathway_id, pathway_items, description = await generate_simple_pathway(user_id, db)
        
        # Insert pathway items
        for item in pathway_items:
            await db.execute(text(
                "INSERT INTO pathway_items (pathway_id, content_id, sequence, weight, prerequisite_ids, completion_status, completion_percentage, time_spent_minutes, success_score) "
                "VALUES (:pathway_id, :content_id, :sequence, :weight, :prerequisite_ids, :completion_status, :completion_percentage, :time_spent_minutes, :success_score)"
            ), {
                "pathway_id": item["pathway_id"],
                "content_id": item["content_id"],
                "sequence": item["sequence"],
                "weight": item["weight"],
                "prerequisite_ids": item["prereqs"],
                "completion_status": item["status"],
                "completion_percentage": item["progress"],
                "time_spent_minutes": item["time"],
                "success_score": item["score"]
            })
        
        # Add skill assessments
        skill_assessments = [
            {"user_id": user_id, "skill_category": "algebra", "proficiency_level": 0.8},
            {"user_id": user_id, "skill_category": "calculus", "proficiency_level": 0.9},
            {"user_id": user_id, "skill_category": "linear_algebra", "proficiency_level": 0.4},
            {"user_id": user_id, "skill_category": "algorithms", "proficiency_level": 0.3},
            {"user_id": user_id, "skill_category": "software_engineering", "proficiency_level": 0.9}
        ]
        
        for assessment in skill_assessments:
            await db.execute(text(
                "INSERT INTO user_skill_assessments (user_id, skill_category, proficiency_level) "
                "VALUES (:user_id, :skill_category, :proficiency_level)"
            ), assessment)
        
        await db.commit()
        print(f"✅ Generated {description} successfully!")
        print(f"   - Pathway ID: {pathway_id}")
        print(f"   - {len(pathway_items)} learning content items")
        print(f"   - {len(skill_assessments)} skill assessments")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate pathway data")
    parser.add_argument("--type", choices=["simple", "complex"], default="simple", 
                       help="Type of pathway: simple (linear) or complex (multi-branch Sankey)")
    args = parser.parse_args()
    
    asyncio.run(generate_pathway_data(args.type))