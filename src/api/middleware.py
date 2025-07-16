"""
Middleware for FastAPI application.

This module provides middleware components for request logging,
error handling, and other cross-cutting concerns.
"""
import time
import uuid
from typing import Callable

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from src.utils.logger import get_logger, set_request_id, set_user_id

# Create module logger
logger = get_logger("api.middleware")

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging all HTTP requests and responses."""
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate request ID if not provided
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        set_request_id(request_id)
        
        # Extract user ID from auth if available
        # This would be expanded based on your auth mechanism
        user_id = None
        if "Authorization" in request.headers:
            # Placeholder for actual auth extraction
            pass
        set_user_id(user_id)
        
        # Log request
        start_time = time.time()
        path = request.url.path
        query_string = str(request.query_params) if request.query_params else ""
        
        logger.info(
            f"Request started: {request.method} {path}",
            extra={
                "method": request.method,
                "path": path,
                "query_string": query_string,
                "client_ip": request.client.host if request.client else None,
                "request_id": request_id,
                "user_id": user_id,
                "user_agent": request.headers.get("User-Agent", ""),
                "referer": request.headers.get("Referer", ""),
                "origin": request.headers.get("Origin", "")
            }
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Log response
            process_time = time.time() - start_time
            status_code = response.status_code
            
            logger.info(
                f"Request completed: {request.method} {path} {status_code}",
                extra={
                    "method": request.method,
                    "path": path,
                    "status_code": status_code,
                    "process_time_ms": round(process_time * 1000, 2),
                    "request_id": request_id,
                    "user_id": user_id
                }
            )
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            return response
            
        except Exception as e:
            # Log unhandled exceptions
            process_time = time.time() - start_time
            logger.error(
                f"Request failed: {request.method} {path}",
                extra={
                    "method": request.method,
                    "path": path,
                    "error": str(e),
                    "process_time_ms": round(process_time * 1000, 2),
                    "request_id": request_id,
                    "user_id": user_id
                },
                exc_info=True
            )
            raise

def setup_middleware(app: FastAPI) -> None:
    """Configure middleware for the FastAPI application."""
    app.add_middleware(RequestLoggingMiddleware)