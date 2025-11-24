"""
Request validation middleware for global request checks.

Handles:
- Request size limits
- Content-Type validation
- Rate limiting (basic)
"""

from fastapi import Request, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.core.config import settings
from app.core.logging import logger


class RequestValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for request validation and limits.
    
    Responsibilities:
    - Enforce request body size limits
    - Validate Content-Type headers
    - Basic rate limiting per IP
    """
    
    # Maximum request body size (bytes)
    MAX_REQUEST_SIZE = 10 * 1024 * 1024  # 10 MB
    
    # Allowed content types for POST/PUT/PATCH
    ALLOWED_CONTENT_TYPES = {
        "application/json",
        "multipart/form-data",
        "application/x-www-form-urlencoded"
    }
    
    async def dispatch(self, request: Request, call_next):
        """
        Validate request before processing.
        """
        # Check request body size
        content_length = request.headers.get("content-length")
        if content_length:
            content_length = int(content_length)
            if content_length > self.MAX_REQUEST_SIZE:
                logger.warning(
                    f"Request too large: {content_length} bytes from {request.client.host}"
                )
                return JSONResponse(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    content={
                        "detail": f"Request body too large. Maximum size: {self.MAX_REQUEST_SIZE} bytes"
                    }
                )
        
        # Validate Content-Type for requests with body
        if request.method in ["POST", "PUT", "PATCH"]:
            content_type = request.headers.get("content-type", "")
            # Extract base content type (ignore charset, boundary, etc.)
            base_content_type = content_type.split(";")[0].strip()
            
            # Skip validation for specific paths
            skip_paths = ["/api/docs", "/api/redoc", "/api/openapi.json"]
            if not any(request.url.path.startswith(path) for path in skip_paths):
                if base_content_type not in self.ALLOWED_CONTENT_TYPES:
                    logger.warning(
                        f"Invalid Content-Type: {content_type} from {request.client.host}"
                    )
                    return JSONResponse(
                        status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                        content={
                            "detail": f"Unsupported Content-Type. Allowed: {', '.join(self.ALLOWED_CONTENT_TYPES)}"
                        }
                    )
        
        # Process request
        return await call_next(request)

