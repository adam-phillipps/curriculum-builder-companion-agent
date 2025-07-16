"""
Unit tests for the logging module.
"""
import json
import logging
from unittest.mock import patch, MagicMock

import pytest

from src.utils.logger import get_logger, set_request_id, set_user_id, log_execution_time


@pytest.fixture
def mock_logger():
    """Create a mock logger for testing."""
    with patch("src.utils.logger.logging.Logger.info") as mock_info, \
         patch("src.utils.logger.logging.Logger.error") as mock_error, \
         patch("src.utils.logger.logging.Logger.debug") as mock_debug:
        yield {
            "info": mock_info,
            "error": mock_error,
            "debug": mock_debug
        }


def test_get_logger():
    """Test that get_logger returns a logger with the correct name."""
    logger = get_logger("test")
    assert isinstance(logger, logging.Logger)
    assert logger.name == "curriculum-builder.test"


def test_set_request_id():
    """Test that set_request_id sets the request ID correctly."""
    # Test with explicit ID
    request_id = "test-id-123"
    result = set_request_id(request_id)
    assert result == request_id
    
    # Test with auto-generated ID
    result = set_request_id()
    assert isinstance(result, str)
    assert len(result) > 0


def test_set_user_id():
    """Test that set_user_id sets the user ID correctly."""
    user_id = 123
    set_user_id(user_id)
    # No return value to check, just ensure it doesn't raise an exception


@pytest.mark.asyncio
async def test_log_execution_time_async(mock_logger):
    """Test that log_execution_time decorator logs execution time for async functions."""
    @log_execution_time
    async def test_async_func():
        return "test"
    
    result = await test_async_func()
    assert result == "test"
    assert mock_logger["info"].called
    
    # Check that the log message contains "executed in"
    args, _ = mock_logger["info"].call_args
    assert "executed in" in args[0]


def test_log_execution_time_sync(mock_logger):
    """Test that log_execution_time decorator logs execution time for sync functions."""
    @log_execution_time
    def test_sync_func():
        return "test"
    
    result = test_sync_func()
    assert result == "test"
    assert mock_logger["info"].called
    
    # Check that the log message contains "executed in"
    args, _ = mock_logger["info"].call_args
    assert "executed in" in args[0]


@pytest.mark.asyncio
async def test_log_execution_time_error(mock_logger):
    """Test that log_execution_time decorator logs errors correctly."""
    @log_execution_time
    async def test_error_func():
        raise ValueError("Test error")
    
    with pytest.raises(ValueError):
        await test_error_func()
    
    assert mock_logger["error"].called
    
    # Check that the log message contains "failed after"
    args, _ = mock_logger["error"].call_args
    assert "failed after" in args[0]