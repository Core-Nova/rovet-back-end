from typing import Optional, List
from pydantic import BaseModel
from app.models.user import UserRole


class TokenPayload(BaseModel):
    """
    Standard JWT token payload structure following RFC 7519.
    
    This model represents the decoded JWT token claims that can be used
    by microservices for authentication and authorization without database lookup.
    """
    # Standard JWT claims (RFC 7519)
    iss: str  # Issuer
    aud: str  # Audience
    exp: int  # Expiration timestamp
    iat: int  # Issued at timestamp
    sub: str  # Subject (user ID)
    jti: str  # JWT ID (unique identifier)
    type: str  # Token type (access, refresh)
    
    # Custom claims for authorization
    role: str  # User role (ADMIN, USER)
    permissions: List[str]  # List of permissions based on role
    
    # Optional user information
    email: Optional[str] = None
    name: Optional[str] = None
    is_active: Optional[bool] = None
    
    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Response model for token endpoints."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # Expiration time in seconds


class RefreshTokenRequest(BaseModel):
    """Request model for refresh token endpoint."""
    refresh_token: str

