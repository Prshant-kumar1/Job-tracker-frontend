"""
Custom middleware for rate limiting, error handling, and security.
"""
import time
from collections import defaultdict
from typing import Dict, Tuple
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging

logger = logging.getLogger(__name__)


# Simple in-memory rate limiter (for production, use Redis)
class RateLimiter:
    """
    Simple token bucket rate limiter.
    
    For production with multiple workers/servers, use Redis-based rate limiting
    (e.g., slowapi library with Redis backend).
    """
    
    def __init__(self):
        # Store: {ip: (tokens, last_update_time)}
        # Start with full bucket (10 tokens) so first request is never denied
        self.buckets: Dict[str, Tuple[float, float]] = defaultdict(lambda: (10.0, time.time()))
        # Cleanup old entries periodically
        self.last_cleanup = time.time()
        
    def is_allowed(
        self, 
        identifier: str, 
        max_requests: int = 10, 
        window_seconds: int = 60
    ) -> bool:
        """
        Check if request is allowed based on token bucket algorithm.
        
        Args:
            identifier: Unique identifier (IP address, user ID, etc.)
            max_requests: Maximum requests allowed in the window
            window_seconds: Time window in seconds
        
        Returns:
            True if request is allowed, False if rate limit exceeded
        """
        current_time = time.time()
        
        # Periodic cleanup (every 5 minutes)
        if current_time - self.last_cleanup > 300:
            self._cleanup_old_entries(current_time)
            self.last_cleanup = current_time
        
        # Get current bucket state
        tokens, last_update = self.buckets[identifier]
        
        # Calculate token refill based on time elapsed
        time_elapsed = current_time - last_update
        refill_rate = max_requests / window_seconds  # tokens per second
        new_tokens = min(max_requests, tokens + time_elapsed * refill_rate)
        
        # Check if we have at least 1 token
        if new_tokens >= 1.0:
            # Consume 1 token
            self.buckets[identifier] = (new_tokens - 1.0, current_time)
            return True
        else:
            # Update state but deny request
            self.buckets[identifier] = (new_tokens, current_time)
            return False
    
    def _cleanup_old_entries(self, current_time: float):
        """Remove entries that haven't been accessed in 1 hour."""
        to_remove = []
        for identifier, (_, last_update) in self.buckets.items():
            if current_time - last_update > 3600:
                to_remove.append(identifier)
        
        for identifier in to_remove:
            del self.buckets[identifier]


# Global rate limiter instance
rate_limiter = RateLimiter()


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware with different limits for different endpoints.
    """
    
    # Define rate limits for different endpoints
    RATE_LIMITS = {
        "/auth/login": (5, 60),      # 5 requests per minute (prevent brute force)
        "/auth/register": (3, 60),   # 3 requests per minute (prevent spam)
        "/applications": (30, 60),   # 30 requests per minute for normal endpoints
        "/dashboard": (20, 60),      # 20 requests per minute for dashboard
        "/ai/suggest": (10, 60),     # 10 requests per minute for AI endpoints
    }
    DEFAULT_LIMIT = (60, 60)  # 60 requests per minute default
    
    async def dispatch(self, request: Request, call_next):
        # Get client identifier (IP address)
        client_ip = request.client.host if request.client else "unknown"
        
        # Skip rate limiting for health check endpoints
        if request.url.path in ["/", "/health"]:
            return await call_next(request)
        
        # Determine rate limit for this endpoint
        max_requests, window_seconds = self.DEFAULT_LIMIT
        for path_prefix, (max_req, window) in self.RATE_LIMITS.items():
            if request.url.path.startswith(path_prefix):
                max_requests, window_seconds = max_req, window
                break
        
        # Check rate limit
        identifier = f"{client_ip}:{request.url.path}"
        if not rate_limiter.is_allowed(identifier, max_requests, window_seconds):
            # Calculate retry time
            retry_after = window_seconds
            
            logger.warning(
                f"Rate limit exceeded for {client_ip} on {request.url.path}"
            )
            
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Rate limit exceeded. Please try again later.",
                    "retry_after": retry_after
                },
                headers={"Retry-After": str(retry_after)}
            )
        
        # Process request
        response = await call_next(request)
        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Global error handling middleware to catch unexpected errors and
    return consistent error responses.
    """
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except HTTPException:
            # Re-raise HTTP exceptions (already handled by FastAPI)
            raise
        except Exception as e:
            # Log the error
            logger.error(
                f"Unhandled exception in {request.method} {request.url.path}",
                exc_info=True
            )
            
            # Return generic error response (don't leak internal details)
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "detail": "An internal server error occurred. Please try again later.",
                    "error_id": str(int(time.time()))  # Simple error ID for tracking
                }
            )


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Add security headers to all responses.
    """
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        # CSP - different policies for dev vs production
        env = os.getenv("ENVIRONMENT", "development")
        if env in ["production", "staging"]:
            # Strict CSP for production
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self'; "
                "style-src 'self'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self' https://*.onrender.com https://*.supabase.co; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'"
            )
        else:
            # Permissive CSP for development (allows Vite HMR, inline scripts/styles)
            response.headers["Content-Security-Policy"] = (
                "default-src 'self' 'unsafe-inline' 'unsafe-eval' data: https:; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' data:; "
                "connect-src 'self' https: wss:; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'"
            )
        
        return response
