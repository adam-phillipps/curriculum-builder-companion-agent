#!/usr/bin/env python3
"""
Generate mock pathway data for Sankey visualization testing.
"""
import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from src.db.database import async_session_maker
from src.db.crud.user import get_user_by_id
from src.db.models.user import User

async def generate_pathway_data():
    """Generate mock pathway data for testing Sankey diagrams."""
    async with async_session_maker() as db:
        # Get first user (should be our test user)
        users = await db.execute("SELECT * FROM users LIMIT 1")
        user = users.fetchone()
        
        if not user:
            print("No users found. Create a user first.")
            return
            
        user_id = user[0]
        print(f"Generating pathway data for user ID: {user_id}")
        
        # Create learning pathway
        pathway_data = {
            "user_id": user_id,
            "name": "Neural Networks Mastery",
            "description": "Complete pathway to build neural networks from scratch",
            "target_outcome": "Build and deploy a neural network from scratch",
            "difficulty_level": "advanced",
            "estimated_duration_hours": 120,
            "completion_percentage": 0.45
        }
        
        await db.execute("""
            INSERT INTO learning_pathways (user_id, name, description, target_outcome, difficulty_level, estimated_duration_hours, completion_percentage)
            VALUES (:user_id, :name, :description, :target_outcome, :difficulty_level, :estimated_duration_hours, :completion_percentage)
        """, pathway_data)
        
        # Get the pathway ID
        pathway_result = await db.execute("SELECT id FROM learning_pathways WHERE user_id = :user_id ORDER BY id DESC LIMIT 1", {"user_id": user_id})
        pathway_id = pathway_result.fetchone()[0]
        
        # Create pathway items (learning content items)
        pathway_items = [
            {"pathway_id": pathway_id, "content_id": 1, "sequence_order": 1, "weight": 0.6, "prerequisite_ids": [], "completion_status": "completed", "completion_percentage": 90, "time_spent_minutes": 180, "success_score": 0.9},
            {"pathway_id": pathway_id, "content_id": 2, "sequence_order": 2, "weight": 0.8, "prerequisite_ids": [1], "completion_status": "completed", "completion_percentage": 75, "time_spent_minutes": 240, "success_score": 0.75},
            {"pathway_id": pathway_id, "content_id": 3, "sequence_order": 3, "weight": 0.7, "prerequisite_ids": [], "completion_status": "in_progress", "completion_percentage": 40, "time_spent_minutes": 120, "success_score": 0.4},
            {"pathway_id": pathway_id, "content_id": 4, "sequence_order": 4, "weight": 0.9, "prerequisite_ids": [3], "completion_status": "completed", "completion_percentage": 85, "time_spent_minutes": 300, "success_score": 0.85},
            {"pathway_id": pathway_id, "content_id": 5, "sequence_order": 5, "weight": 0.7, "prerequisite_ids": [4], "completion_status": "in_progress", "completion_percentage": 60, "time_spent_minutes": 150, "success_score": 0.6},
            {"pathway_id": pathway_id, "content_id": 6, "sequence_order": 6, "weight": 1.0, "prerequisite_ids": [2, 5], "completion_status": "not_started", "completion_percentage": 0, "time_spent_minutes": 0, "success_score": None}
        ]
        
        for item in pathway_items:
            await db.execute("""
                INSERT INTO pathway_items (pathway_id, content_id, sequence_order, weight, prerequisite_ids, completion_status, completion_percentage, time_spent_minutes, success_score)
                VALUES (:pathway_id, :content_id, :sequence_order, :weight, :prerequisite_ids, :completion_status, :completion_percentage, :time_spent_minutes, :success_score)
            """, {**item, "prerequisite_ids": str(item["prerequisite_ids"])})
        
        # Create skill assessments
        skill_assessments = [
            {"user_id": user_id, "skill_category": "algebra", "proficiency_level": 0.8},
            {"user_id": user_id, "skill_category": "calculus", "proficiency_level": 0.9},
            {"user_id": user_id, "skill_category": "linear_algebra", "proficiency_level": 0.4},
            {"user_id": user_id, "skill_category": "algorithms", "proficiency_level": 0.3},
            {"user_id": user_id, "skill_category": "software_engineering", "proficiency_level": 0.9},
            {"user_id": user_id, "skill_category": "devops", "proficiency_level": 0.8}
        ]
        
        for assessment in skill_assessments:
            await db.execute("""
                INSERT INTO user_skill_assessments (user_id, skill_category, proficiency_level)
                VALUES (:user_id, :skill_category, :proficiency_level)
            """, assessment)
        
        await db.commit()
        print(f"✅ Generated pathway data successfully!")
        print(f"   - Pathway ID: {pathway_id}")
        print(f"   - {len(pathway_items)} learning content items")
        print(f"   - {len(skill_assessments)} skill assessments")

if __name__ == "__main__":
    asyncio.run(generate_pathway_data())