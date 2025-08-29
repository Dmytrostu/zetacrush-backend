"""
Custom middleware for request logging and other middleware functionality.

This module contains middleware components that can be added to the FastAPI application.
"""
import time
import logging
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware for logging HTTP requests and responses.
    
    Logs the method, path, status code, processing time, and client IP for each request.
    """
    
    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.time()
        
        # Get client IP, considering possible proxy headers
        client_host = request.client.host if request.client else "unknown"
        forwarded_for = request.headers.get("x-forwarded-for")
        client_ip = forwarded_for.split(",")[0] if forwarded_for else client_host
        
        # Log the request
        logger.info(
            f"Request: {request.method} {request.url.path} - "
            f"Client: {client_ip}"
        )
        
        # Process the request
        response = await call_next(request)
        
        # Calculate processing time
        process_time = time.time() - start_time
        
        # Log the response
        logger.info(
            f"Response: {request.method} {request.url.path} - "
            f"Status: {response.status_code} - "
            f"Time: {process_time:.3f}s - "
            f"Client: {client_ip}"
        )
        
        # Add custom header with processing time
        response.headers["X-Process-Time"] = f"{process_time:.3f}"
        
        return response
