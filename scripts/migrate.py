#!/usr/bin/env python3
"""
Database migration script for startup.
Runs Alembic migrations before starting the FastAPI application.
"""
import os
import subprocess
import sys
import time
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def run_migrations():
    """Run Alembic migrations."""
    print("🔄 Running database migrations...")
    
    try:
        # Run migrations from /app directory where alembic.ini is located
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            cwd="/app",
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("✅ Database migrations completed successfully")
            if result.stdout:
                print(f"Migration output: {result.stdout}")
            return True
        else:
            print(f"❌ Migration failed with return code {result.returncode}")
            if result.stderr:
                print(f"Error output: {result.stderr}")
            if result.stdout:
                print(f"Standard output: {result.stdout}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Migration timed out after 60 seconds")
        return False
    except Exception as e:
        print(f"❌ Migration error: {e}")
        return False

def get_database_url():
    """Get database URL from environment variables."""
    # Try DATABASE_URL first (for local development)
    database_url = os.getenv('DATABASE_URL')
    if database_url:
        # Convert async URL to sync for psycopg2
        if "postgresql+asyncpg://" in database_url:
            return database_url.replace("postgresql+asyncpg://", "postgresql://")
        return database_url
    
    # Build from individual components (for AWS)
    host = os.getenv('POSTGRES_HOST')
    port = os.getenv('POSTGRES_PORT', '5432')
    database = os.getenv('POSTGRES_DB')
    user = os.getenv('POSTGRES_USER')
    password = os.getenv('POSTGRES_PASSWORD')
    
    if not all([host, database, user, password]):
        raise ValueError("Missing required database environment variables")
    
    return f"postgresql://{user}:{password}@{host}:{port}/{database}"

def wait_for_db():
    """Wait for database to be ready."""
    print("⏳ Waiting for database to be ready...")
    
    # Use simple environment-based config
    try:
        db_url = get_database_url()
        print(f"🔧 Database config:")
        print(f"   Host: {os.getenv('POSTGRES_HOST')}")
        print(f"   Port: {os.getenv('POSTGRES_PORT')}")
        print(f"   Database: {os.getenv('POSTGRES_DB')}")
        print(f"   User: {os.getenv('POSTGRES_USER')}")
    except Exception as e:
        print(f"❌ Config error: {e}")
        return False
    
    max_retries = 30
    for i in range(max_retries):
        try:
            from sqlalchemy import create_engine, text
            engine = create_engine(db_url, connect_args={"connect_timeout": 5})
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            print("✅ Database is ready")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            time.sleep(2)
        
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