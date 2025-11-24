"""
Authentication Data Transfer Objects (DTOs).

Defines API contracts for authentication endpoints.
"""

from pydantic import BaseModel, EmailStr, Field
from app.models.user import UserRole


class LoginRequest(BaseModel):
    """Login request model."""
    
    email: EmailStr = Field(
        ...,
        description="User email address",
        examples=["user@example.com"]
    )
    password: str = Field(
        ...,
        min_length=1,
        description="User password",
        examples=["password123"]
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePass123!"
            }
        }


class TokenResponse(BaseModel):
    """JWT token response model."""
    
    access_token: str = Field(
        ...,
        description="JWT access token",
        examples=["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."]
    )
    token_type: str = Field(
        default="bearer",
        description="Token type (always 'bearer')",
        examples=["bearer"]
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class TokenPayload(BaseModel):
    """JWT token payload model (internal use)."""
    
    sub: int = Field(
        ...,
        description="Subject (user ID)",
        examples=[1]
    )
    role: UserRole = Field(
        ...,
        description="User role",
        examples=["user", "admin"]
    )
    exp: int = Field(
        ...,
        description="Expiration timestamp",
        examples=[1735689600]
    )
