#!/usr/bin/env python3
"""Generate the ideal Sankey pathway data structure."""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from src.db.database import async_session_maker

async def generate_sankey_data():
    """Generate complete Sankey pathway data for neural networks learning goal."""
    async with async_session_maker() as db:
        # Get John Doe (our test user)
        result = await db.execute(text("SELECT id FROM users WHERE first_name = 'John' LIMIT 1"))
        user_row = result.fetchone()
        
        if not user_row:
            print("No user 'John' found. Create a user first.")
            return
            
        user_id = user_row[0]
        print(f"Generating Sankey data for user ID: {user_id} (John Doe)")
        
        # 1. Create the Neural Networks pathway
        await db.execute(text(
            "INSERT INTO learning_pathways (user_id, name, description, target_persona, estimated_duration, total_cost, completion_percentage) "
            "VALUES (:user_id, :name, :description, :target_persona, :duration, :cost, :completion)"
        ), {
            "user_id": user_id,
            "name": "Neural Networks Mastery",
            "description": "Complete pathway from math foundations to building neural networks from scratch",
            "target_persona": "ml_engineer", 
            "duration": 120,
            "cost": 0.0,
            "completion": 45.0
        })
        
        # Get the pathway ID
        result = await db.execute(text("SELECT id FROM learning_pathways WHERE user_id = :user_id ORDER BY id DESC LIMIT 1"), {"user_id": user_id})
        pathway_id = result.fetchone()[0]
        
        # 2. Create pathway items (learning content) with proper Sankey structure
        pathway_items = [
            # Math Foundation Branch
            {"pathway_id": pathway_id, "content_id": 1, "sequence": 1, "weight": 0.6, "prereqs": "[]", "status": "completed", "progress": 90, "time": 180, "score": 0.9},
            {"pathway_id": pathway_id, "content_id": 2, "sequence": 2, "weight": 0.8, "prereqs": "[1]", "status": "completed", "progress": 75, "time": 240, "score": 0.75},
            
            # CS Foundation Branch  
            {"pathway_id": pathway_id, "content_id": 3, "sequence": 3, "weight": 0.7, "prereqs": "[]", "status": "in_progress", "progress": 40, "time": 120, "score": 0.4},
            {"pathway_id": pathway_id, "content_id": 4, "sequence": 4, "weight": 0.9, "prereqs": "[3]", "status": "completed", "progress": 85, "time": 200, "score": 0.85},
            
            # Engineering Branch
            {"pathway_id": pathway_id, "content_id": 5, "sequence": 5, "weight": 0.7, "prereqs": "[4]", "status": "in_progress", "progress": 60, "time": 150, "score": 0.6},
            
            # Final Target (converges from multiple branches)
            {"pathway_id": pathway_id, "content_id": 6, "sequence": 6, "weight": 1.0, "prereqs": "[2,5]", "status": "not_started", "progress": 0, "time": 0, "score": None}
        ]
        
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
        
        await db.commit()
        print(f"✅ Generated complete Sankey pathway:")
        print(f"   - Pathway ID: {pathway_id}")
        print(f"   - {len(pathway_items)} learning content items")
        print(f"   - Multi-branch flow: Math + CS + Engineering → Neural Networks")
        print(f"   - Weighted connections based on skill assessments")
        print(f"   - Ready for Sankey visualization!")

if __name__ == "__main__":
    asyncio.run(generate_sankey_data())