from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.core.config import settings


class SecurityMiddleware(BaseHTTPMiddleware):
    async def set_security_headers(self, response: Response):
        """Set security headers for all responses"""
        # XSS Protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Frame Options (prevent clickjacking)
        response.headers["X-Frame-Options"] = "DENY"

    async def dispatch(self, request: Request, call_next):
        # Process request
        response = await call_next(request)
        
        # Add security headers
        await self.set_security_headers(response)
        
        return response 