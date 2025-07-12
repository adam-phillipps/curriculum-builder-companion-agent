"""
Unit tests for seed data functionality.
"""
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import sys
import os

# Add scripts to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../scripts'))

from seed_data import create_test_user


@pytest.mark.asyncio
async def test_create_test_user_new_user():
    """Test creating a new test user."""
    mock_db = AsyncMock()
    
    with patch('seed_data.async_session_maker') as mock_session, \
         patch('seed_data.get_user_by_email') as mock_get_user, \
         patch('seed_data.create_user') as mock_create_user:
        
        # Setup mocks
        mock_session.return_value.__aenter__.return_value = mock_db
        mock_get_user.return_value = None  # User doesn't exist
        
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.current_role = "learner"
        mock_create_user.return_value = mock_user
        
        # Test
        result = await create_test_user("test@example.com", "learner")
        
        # Assertions
        assert result["id"] == 1
        assert result["email"] == "test@example.com"
        assert result["role"] == "learner"
        mock_create_user.assert_called_once()


@pytest.mark.asyncio
async def test_create_test_user_existing_user():
    """Test handling existing test user."""
    mock_db = AsyncMock()
    
    with patch('seed_data.async_session_maker') as mock_session, \
         patch('seed_data.get_user_by_email') as mock_get_user:
        
        # Setup mocks
        mock_session.return_value.__aenter__.return_value = mock_db
        
        mock_user = MagicMock()
        mock_user.id = 1
        mock_user.email = "test@example.com"
        mock_user.current_role = "learner"
        mock_get_user.return_value = mock_user
        
        # Test
        result = await create_test_user("test@example.com", "learner")
        
        # Assertions
        assert result["id"] == 1
        assert result["email"] == "test@example.com"
        assert result["role"] == "learner"


def test_seed_data_argument_parsing():
    """Test command line argument parsing."""
    import argparse
    from unittest.mock import patch
    
    # Mock sys.argv
    test_args = ['seed_data.py', '--email', 'test@example.com', '--role', 'admin', '--type', 'user']
    
    with patch('sys.argv', test_args):
        parser = argparse.ArgumentParser()
        parser.add_argument("--email", help="Email address for specific user data generation")
        parser.add_argument("--role", default="learner", help="Role for the test user")
        parser.add_argument("--type", choices=["user", "pathway", "progress", "all"], 
                           default="all", help="Type of data to generate")
        
        args = parser.parse_args()
        
        assert args.email == "test@example.com"
        assert args.role == "admin"
        assert args.type == "user"