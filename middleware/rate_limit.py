"""
Rate limiting middleware for the FastAPI application.

This module contains middleware for implementing rate limiting to protect the API
from excessive requests.
"""
import time
from typing import Dict, Tuple, List, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)

class RateLimiter:
    """
    Simple in-memory rate limiter.
    
    This class implements a sliding window rate limiter to track requests per client.
    """
    def __init__(self, window_size: int = 60, max_requests: int = 30):
        """
        Initialize the rate limiter.
        
        Args:
            window_size (int): The time window in seconds to track requests.
            max_requests (int): Maximum number of requests allowed in the window.
        """
        self.window_size = window_size
        self.max_requests = max_requests
        self.requests: Dict[str, List[float]] = {}
    
    def is_rate_limited(self, client_id: str) -> Tuple[bool, int, int]:
        """
        Check if a client is rate limited.
        
        Args:
            client_id (str): The client identifier (e.g., IP address).
            
        Returns:
            Tuple[bool, int, int]: A tuple containing (is_limited, remaining_requests, retry_after)
        """
        now = time.time()
        
        # Initialize client requests if not present
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        # Remove timestamps outside the window
        self.requests[client_id] = [ts for ts in self.requests[client_id] if now - ts <= self.window_size]
        
        # Check if client has exceeded rate limit
        if len(self.requests[client_id]) >= self.max_requests:
            # Calculate the retry-after time in seconds
            oldest_request = min(self.requests[client_id])
            retry_after = int(self.window_size - (now - oldest_request))
            return True, 0, max(1, retry_after)
        
        # Add current request timestamp
        self.requests[client_id].append(now)
        
        # Calculate remaining requests
        remaining = self.max_requests - len(self.requests[client_id])
        return False, remaining, 0
    
    def cleanup(self):
        """
        Clean up expired entries to prevent memory growth.
        """
        now = time.time()
        for client_id in list(self.requests.keys()):
            self.requests[client_id] = [ts for ts in self.requests[client_id] if now - ts <= self.window_size]
            if not self.requests[client_id]:
                del self.requests[client_id]

class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware for implementing rate limiting.
    
    This middleware limits the number of requests a client can make within a specified time window.
    """
    def __init__(self, app, window_size: int = 60, max_requests: int = 30, exclude_paths: Optional[List[str]] = None):
        """
        Initialize the rate limit middleware.
        
        Args:
            app: The FastAPI application.
            window_size (int): The time window in seconds to track requests.
            max_requests (int): Maximum number of requests allowed in the window.
            exclude_paths (List[str], optional): List of paths to exclude from rate limiting.
        """
        super().__init__(app)
        self.limiter = RateLimiter(window_size, max_requests)
        self.exclude_paths = exclude_paths or ["/docs", "/redoc", "/openapi.json", "/static/"]
        self.cleanup_counter = 0
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip rate limiting for excluded paths
        path = request.url.path
        if any(path.startswith(excluded) for excluded in self.exclude_paths):
            return await call_next(request)
        
        # Get client IP, considering possible proxy headers
        client_host = request.client.host if request.client else "unknown"
        forwarded_for = request.headers.get("x-forwarded-for")
        client_ip = forwarded_for.split(",")[0] if forwarded_for else client_host
        
        # Check if client is rate limited
        is_limited, remaining, retry_after = self.limiter.is_rate_limited(client_ip)
        
        # Perform periodic cleanup (every 100 requests)
        self.cleanup_counter += 1
        if self.cleanup_counter >= 100:
            self.limiter.cleanup()
            self.cleanup_counter = 0
        
        # Apply rate limiting if needed
        if is_limited:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}, path: {path}")
            headers = {
                "Retry-After": str(retry_after),
                "X-RateLimit-Limit": str(self.limiter.max_requests),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(int(time.time()) + retry_after),
            }
            
            return Response(
                content='{"detail":"Too many requests. Please try again later."}',
                status_code=429,
                media_type="application/json",
                headers=headers
            )
        
        # Add rate limit headers
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(self.limiter.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(time.time()) + self.limiter.window_size)
        
        return response
