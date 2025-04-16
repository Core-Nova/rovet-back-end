from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

class SecurityMiddleware(BaseHTTPMiddleware):
    async def set_security_headers(self, response: Response):
        """Set security headers for all responses"""
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        response.headers["X-Frame-Options"] = "DENY"

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        await self.set_security_headers(response)
        
        return response 