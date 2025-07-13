#!/usr/bin/env python3
"""
Debug script to check user progress data for graph display issues.
Run this to see what data is actually being returned.
"""
import asyncio
import sys
import os
sys.path.append('/Users/adam/code/curriculum-builder-companion-agent')

from src.db.database import get_db
from src.db.crud.user import get_user_content_progress, get_users
from src.db.models.user import UserContentProgress

async def debug_user_progress():
    """Check what progress data exists for users."""
    async for db in get_db():
        try:
            # Get all users
            users = await get_users(db, limit=10)
            print(f"Found {len(users)} users")
            
            for user in users:
                print(f"\n=== User {user.id}: {user.first_name} {user.last_name} ===")
                print(f"Role: {user.current_role}")
                
                # Get progress for this user
                progress_records = await get_user_content_progress(db, user.id)
                print(f"Progress records: {len(progress_records)}")
                
                if progress_records:
                    for progress in progress_records:
                        print(f"  Content {progress.content_id}: {progress.status} - {progress.progress_percentage}% - {progress.comprehension_percentage}% comprehension")
                        print(f"    Time spent: {progress.time_spent_minutes} minutes")
                        print(f"    Started: {progress.started_at}, Completed: {progress.completed_at}")
                else:
                    print("  No progress records found!")
                    
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            break

if __name__ == "__main__":
    asyncio.run(debug_user_progress())