#!/usr/bin/env python3
"""
Generate user content progress data for testing.
Creates realistic progress data for learning content items.
"""
import asyncio
import sys
import os
from sqlalchemy import text
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.db.database import async_session_maker

async def generate_content_progress(user_id: int = 1, content_ids: list = None):
    """
    Generate user content progress data for specified content items.
    
    Parameters
    ----------
    user_id : int
        The user ID to create progress for (default: 1)
    content_ids : list
        List of content IDs to create progress for. If None, uses tree structure (101-106)
    
    Returns
    -------
    None
        Creates progress records in the database
    """
    async with async_session_maker() as db:
        # Get user information
        result = await db.execute(text("SELECT first_name, last_name, email FROM users WHERE id = :user_id"), {"user_id": user_id})
        user_row = result.fetchone()
        
        if not user_row:
            print(f"❌ User ID {user_id} not found!")
            return
            
        first_name, last_name, email = user_row
        
        # Default to tree structure content IDs if not specified
        if content_ids is None:
            content_ids = [101, 102, 103, 104, 105, 106]
        
        print(f"\n📊 Generating content progress for:")
        print(f"   User ID: {user_id}")
        print(f"   Name: {first_name} {last_name}")
        print(f"   Email: {email}")
        print(f"   Content IDs: {content_ids}\n")
        
        # Clear existing progress for this user and these content items
        await db.execute(text(
            'DELETE FROM user_content_progress WHERE user_id = :user_id AND content_id = ANY(:content_ids)'
        ), {'user_id': user_id, 'content_ids': content_ids})
        
        # Create tree structure progress data
        progress_data = [
            # Leaf nodes (no prerequisites) - completed
            {'user_id': user_id, 'content_id': 101, 'status': 'completed', 'progress_percentage': 100, 'time_spent_minutes': 120},
            {'user_id': user_id, 'content_id': 103, 'status': 'completed', 'progress_percentage': 90, 'time_spent_minutes': 150},
            
            # Intermediate nodes - mostly completed
            {'user_id': user_id, 'content_id': 102, 'status': 'completed', 'progress_percentage': 85, 'time_spent_minutes': 180},
            {'user_id': user_id, 'content_id': 104, 'status': 'in_progress', 'progress_percentage': 60, 'time_spent_minutes': 100},
            
            # Higher level - in progress
            {'user_id': user_id, 'content_id': 105, 'status': 'in_progress', 'progress_percentage': 40, 'time_spent_minutes': 80},
            
            # Root node (final goal) - not started
            {'user_id': user_id, 'content_id': 106, 'status': 'not_started', 'progress_percentage': 0, 'time_spent_minutes': 0}
        ]
        
        # Filter progress data to only include requested content IDs
        filtered_progress = [p for p in progress_data if p['content_id'] in content_ids]
        
        for progress in filtered_progress:
            await db.execute(text(
                'INSERT INTO user_content_progress (user_id, content_id, status, progress_percentage, time_spent_minutes, started_at, last_accessed_at, created_at, updated_at) '
                'VALUES (:user_id, :content_id, :status, :progress_percentage, :time_spent_minutes, NOW(), NOW(), NOW(), NOW())'
            ), progress)
        
        await db.commit()
        print(f"✅ Generated progress data for {first_name} {last_name} ({email})")
        print(f"   - User ID: {user_id}")
        print(f"   - Content IDs: {[p['content_id'] for p in filtered_progress]}")
        print(f"   - Progress mix: {len([p for p in filtered_progress if p['status'] == 'completed'])} completed, "
              f"{len([p for p in filtered_progress if p['status'] == 'in_progress'])} in progress, "
              f"{len([p for p in filtered_progress if p['status'] == 'not_started'])} not started")
        print(f"\n👤 Data created for: {first_name} {last_name} (ID: {user_id})")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate user content progress data")
    parser.add_argument("--user-id", type=int, default=1, 
                       help="User ID to create progress for (default: 1)")
    parser.add_argument("--content-ids", nargs='+', type=int, 
                       help="Content IDs to create progress for (default: 101-106)")
    args = parser.parse_args()
    
    asyncio.run(generate_content_progress(args.user_id, args.content_ids))