"""
Structured logging module for application-wide use.

This module provides a consistent logging interface that outputs structured JSON logs,
supports correlation IDs for request tracing, and integrates with both local development
and AWS CloudWatch environments.
"""
import json
import logging
import sys
import time
import uuid
from contextvars import ContextVar
from functools import wraps
from typing import Any, Callable, Dict, Optional, Union

from src.config import get_settings

settings = get_settings()

# Context variables for request tracking
request_id_var: ContextVar[str] = ContextVar("request_id", default="")
user_id_var: ContextVar[Optional[int]] = ContextVar("user_id", default=None)

# Configure root logger
root_logger = logging.getLogger()

# Set log level from environment or config
log_level_name = settings.LOG_LEVEL.upper()
log_level = getattr(logging, log_level_name, logging.INFO)
if settings.DEBUG and log_level > logging.DEBUG:
    log_level = logging.DEBUG

root_logger.setLevel(log_level)

# Remove existing handlers to avoid duplicates
for handler in root_logger.handlers[:]:
    root_logger.removeHandler(handler)

# Create console handler
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(log_level)


class JsonFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "message": record.getMessage(),
            "logger": record.name,
            "path": record.pathname,
            "function": record.funcName,
            "line": record.lineno,
            "app_env": settings.APP_ENV,
        }
        
        # Add request_id if available
        request_id = request_id_var.get()
        if request_id:
            log_data["request_id"] = request_id
            
        # Add user_id if available
        user_id = user_id_var.get()
        if user_id:
            log_data["user_id"] = user_id
            
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
            
        # Add extra fields from record
        if hasattr(record, "extra"):
            log_data.update(record.extra)
            
        return json.dumps(log_data)


# Set formatter for console handler
console_handler.setFormatter(JsonFormatter())
root_logger.addHandler(console_handler)

# Create module-level logger
logger = logging.getLogger("curriculum-builder")


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name."""
    return logging.getLogger(f"curriculum-builder.{name}")


def set_request_id(request_id: Optional[str] = None) -> str:
    """Set request ID for the current context."""
    if request_id is None:
        request_id = str(uuid.uuid4())
    request_id_var.set(request_id)
    return request_id


def set_user_id(user_id: Optional[int]) -> None:
    """Set user ID for the current context."""
    user_id_var.set(user_id)


def log_execution_time(func: Callable) -> Callable:
    """Decorator to log function execution time."""
    @wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(
                f"Function {func.__name__} executed in {execution_time:.2f}s",
                extra={"execution_time": execution_time}
            )
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                f"Function {func.__name__} failed after {execution_time:.2f}s: {str(e)}",
                extra={"execution_time": execution_time},
                exc_info=True
            )
            raise
    
    @wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            logger.info(
                f"Function {func.__name__} executed in {execution_time:.2f}s",
                extra={"execution_time": execution_time}
            )
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                f"Function {func.__name__} failed after {execution_time:.2f}s: {str(e)}",
                extra={"execution_time": execution_time},
                exc_info=True
            )
            raise
    
    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper


# Add missing import
import asyncio