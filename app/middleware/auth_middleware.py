"""
Authentication middleware for JWT validation.

REFACTORED:
- Removed database session creation from middleware
- Reduced logging noise
- Simplified logic
- Authentication now handled by FastAPI dependencies
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings
from app.core.logging import logger


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Authentication middleware for global auth check.
    
    Note: This middleware primarily checks for public paths.
    Actual authentication is handled by FastAPI dependencies (get_current_user).
    
    Responsibilities:
    - Allow public paths without authentication
    - Reject requests to protected paths without Bearer token
    - Actual token validation is done in dependencies (separation of concerns)
    """
    
    # Public paths that don't require authentication
    PUBLIC_PATHS = {
        "/",
        "/health",
        "/api/health",
        "/api/metrics",
        "/api/docs",
        "/api/redoc",
        "/api/openapi.json",
        f"{settings.API_V1_STR}/auth/login",
        f"{settings.API_V1_STR}/auth/register",
        f"{settings.API_V1_STR}/health",
        f"{settings.API_V1_STR}/metrics",
        f"{settings.API_V1_STR}/openapi.json",
    }
    
    async def dispatch(self, request: Request, call_next):
        """
        Check if request path is public or has Bearer token.
        
        For protected paths:
        - Verify Authorization header exists and has Bearer prefix
        - Actual token validation done in dependency injection
        
        For public paths:
        - Skip authentication entirely
        """
        path = request.url.path
        
        # Allow public paths
        if self._is_public_path(path):
            return await call_next(request)
        
        # Check for Authorization header
        auth_header = request.headers.get("Authorization")
        
        if not auth_header or not auth_header.startswith("Bearer "):
            logger.warning(f"Missing or invalid auth header for path: {path}")
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing or invalid authentication token"}
            )
        
        # Token is present - actual validation happens in dependencies
        return await call_next(request)
    
    def _is_public_path(self, path: str) -> bool:
        """
        Check if path is public (doesn't require authentication).
        
        Args:
            path: Request path
            
        Returns:
            bool: True if public, False if protected
        """
        # Exact match
        if path in self.PUBLIC_PATHS:
            return True
        
        # Static files
        if path.startswith("/static/"):
            return True
        
        # Docs paths
        if path.startswith("/docs") or path.startswith("/redoc"):
            return True
        
        return False


class AdminMiddleware(BaseHTTPMiddleware):
    """
    Admin authorization middleware.
    
    Note: This is mostly replaced by get_current_admin_user dependency.
    Keeping for backwards compatibility and defense in depth.
    """
    
    async def dispatch(self, request: Request, call_next):
        """
        Check admin authorization for admin routes.
        
        Note: Actual admin check is done in get_current_admin_user dependency.
        This middleware provides an additional layer of defense.
        """
        path = request.url.path
        admin_base_path = f"{settings.API_V1_STR}/users"
        
        # Not an admin route - skip check
        if not path.startswith(admin_base_path):
            return await call_next(request)
        
        # Admin route - user must be set by AuthMiddleware
        # Actual admin role check is done in dependencies
        if not hasattr(request.state, "user"):
            logger.warning(f"No user in request state for admin path: {path}")
            return JSONResponse(
                status_code=401,
                content={"detail": "Authentication required"}
            )
        
        return await call_next(request)
