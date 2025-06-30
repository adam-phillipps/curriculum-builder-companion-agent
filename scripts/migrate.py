#!/usr/bin/env python3
"""
Database migration script for startup.
Runs Alembic migrations before starting the FastAPI application.
"""
import subprocess
import sys
import time
from pathlib import Path

def run_migrations():
    """Run Alembic migrations."""
    print("🔄 Running database migrations...")
    
    try:
        # Change to app directory
        app_dir = Path(__file__).parent.parent
        
        # Run migrations
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd=app_dir,
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("✅ Database migrations completed successfully")
            return True
        else:
            print(f"❌ Migration failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Migration timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"❌ Migration error: {e}")
        return False

def wait_for_db():
    """Wait for database to be ready."""
    print("⏳ Waiting for database to be ready...")
    
    max_retries = 30
    for i in range(max_retries):
        try:
            result = subprocess.run(
                ["python", "-c", "from src.config import get_settings; from sqlalchemy import create_engine; engine = create_engine(str(get_settings().DATABASE_URL).replace('postgresql+asyncpg://', 'postgresql://')); engine.connect()"],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                print("✅ Database is ready")
                return True
        except:
            pass
        
        print(f"⏳ Database not ready, retrying... ({i+1}/{max_retries})")
        time.sleep(2)
    
    print("❌ Database failed to become ready")
    return False

if __name__ == "__main__":
    if not wait_for_db():
        sys.exit(1)
    
    if not run_migrations():
        sys.exit(1)
    
    print("🚀 Ready to start application")