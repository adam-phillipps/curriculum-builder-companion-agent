#!/usr/bin/env python3
"""
Unified data seeding script for curriculum builder.
Can generate data for specific users or all users.
"""
import asyncio
import argparse
import os
import sys
from typing import Optional

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.db.database import async_session_maker
from src.db.crud.user import create_user, get_user_by_email
from src.api.schemas.user import UserCreate


async def create_test_user(email: str, role: str = "learner") -> dict:
    """Create a test user with specified email."""
    async with async_session_maker() as db:
        # Check if user already exists
        existing_user = await get_user_by_email(db, email)
        if existing_user:
            print(f"User {email} already exists (ID: {existing_user.id})")
            return {"id": existing_user.id, "email": existing_user.email, "role": existing_user.current_role}
        
        # Create new user
        user_data = UserCreate(
            first_name="Test",
            last_name="User",
            email=email,
            current_role=role
        )
        
        user = await create_user(db, user_data)
        print(f"Created user: {user.email} (ID: {user.id}, Role: {user.current_role})")
        return {"id": user.id, "email": user.email, "role": user.current_role}


async def generate_pathway_data(user_id: Optional[int] = None):
    """Generate pathway data for specific user or all users."""
    # Import and run existing pathway generation
    from generate_pathway_data import generate_pathway_data as generate_pathways
    await generate_pathways("complex")
    print("✅ Pathway data generated")


async def generate_progress_data(user_id: Optional[int] = None):
    """Generate progress data for specific user or all users."""
    # Import and run existing progress generation  
    from generate_content_progress import generate_content_progress
    await generate_content_progress()
    print("✅ Progress data generated")


async def main():
    parser = argparse.ArgumentParser(description="Seed database with test data")
    parser.add_argument("--email", help="Email address for specific user data generation")
    parser.add_argument("--role", default="learner", help="Role for the test user")
    parser.add_argument("--type", choices=["user", "pathway", "progress", "all"], 
                       default="all", help="Type of data to generate")
    
    args = parser.parse_args()
    
    user_id = None
    
    # Create or get specific user if email provided
    if args.email:
        user_info = await create_test_user(args.email, args.role)
        user_id = user_info["id"]
        print(f"Working with user: {user_info['email']} (ID: {user_id})")
    
    # Generate requested data types
    if args.type in ["user", "all"] and args.email:
        print("✅ User created/verified")
    
    if args.type in ["pathway", "all"]:
        await generate_pathway_data(user_id)
    
    if args.type in ["progress", "all"]:
        await generate_progress_data(user_id)
    
    print("🎉 Data seeding completed!")


if __name__ == "__main__":
    asyncio.run(main())