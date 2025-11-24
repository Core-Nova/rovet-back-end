"""
User Data Transfer Objects (DTOs) with enhanced validation.

These models define the API contracts for user-related operations.
All validation rules are centralized here using Pydantic validators.
"""

from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional, List
from datetime import datetime
import re

from app.models.user import UserRole


class UserBase(BaseModel):
    """Base user model with common fields."""
    
    email: EmailStr = Field(
        ...,
        description="User email address (must be valid email format)",
        examples=["user@example.com"]
    )
    full_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="User's full name",
        examples=["John Doe"]
    )
    
    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v: str) -> str:
        """Validate full name format."""
        if not v or not v.strip():
            raise ValueError('Full name cannot be empty or whitespace')
        
        # Remove excessive whitespace
        v = ' '.join(v.split())
        
        # Check for minimum meaningful length
        if len(v) < 2:
            raise ValueError('Full name must be at least 2 characters')
        
        return v


class UserCreate(UserBase):
    """User creation model with password validation."""
    
    password: str = Field(
        ...,
        min_length=8,
        max_length=100,
        description="User password (min 8 chars, must include uppercase, lowercase, number)",
        examples=["SecurePass123!"]
    )
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        """
        Validate password complexity.
        
        Requirements:
        - At least 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one number
        - At least one special character (optional but recommended)
        """
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if len(v) > 100:
            raise ValueError('Password must be at most 100 characters long')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        
        # Check for common weak passwords
        weak_passwords = {
            'password', 'password123', '12345678', 'qwerty123',
            'admin123', 'letmein123', 'welcome123'
        }
        if v.lower() in weak_passwords:
            raise ValueError('Password is too common. Please choose a stronger password')
        
        return v


class UserUpdate(BaseModel):
    """
    User update model - all fields optional.
    
    Only provided fields will be updated (partial update support).
    """
    
    email: Optional[EmailStr] = Field(
        None,
        description="New email address",
        examples=["newemail@example.com"]
    )
    full_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="New full name",
        examples=["Jane Doe"]
    )
    password: Optional[str] = Field(
        None,
        min_length=8,
        max_length=100,
        description="New password",
        examples=["NewSecurePass123!"]
    )
    role: Optional[UserRole] = Field(
        None,
        description="New user role (admin only)",
        examples=["user", "admin"]
    )
    is_active: Optional[bool] = Field(
        None,
        description="User active status (admin only)",
        examples=[True, False]
    )
    
    @field_validator('full_name')
    @classmethod
    def validate_full_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate full name if provided."""
        if v is None:
            return v
        
        if not v.strip():
            raise ValueError('Full name cannot be empty or whitespace')
        
        v = ' '.join(v.split())
        
        if len(v) < 2:
            raise ValueError('Full name must be at least 2 characters')
        
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: Optional[str]) -> Optional[str]:
        """Validate password if provided."""
        if v is None:
            return v
        
        # Same validation as UserCreate
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        
        if len(v) > 100:
            raise ValueError('Password must be at most 100 characters long')
        
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        
        weak_passwords = {
            'password', 'password123', '12345678', 'qwerty123',
            'admin123', 'letmein123', 'welcome123'
        }
        if v.lower() in weak_passwords:
            raise ValueError('Password is too common. Please choose a stronger password')
        
        return v


class UserResponse(BaseModel):
    """User response model - what API returns."""
    
    id: int = Field(..., description="User ID", examples=[1])
    email: EmailStr = Field(..., description="User email", examples=["user@example.com"])
    full_name: str = Field(..., description="User's full name", examples=["John Doe"])
    role: UserRole = Field(..., description="User role", examples=["user", "admin"])
    is_active: bool = Field(..., description="User active status", examples=[True])
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")

    class Config:
        from_attributes = True


class UserFilter(BaseModel):
    """Filter parameters for user queries."""
    
    email: Optional[str] = Field(
        None,
        description="Filter by email (partial match, case-insensitive)",
        examples=["john", "example.com"]
    )
    role: Optional[UserRole] = Field(
        None,
        description="Filter by exact role",
        examples=["user", "admin"]
    )
    is_active: Optional[bool] = Field(
        None,
        description="Filter by active status",
        examples=[True, False]
    )


class PaginatedUserResponse(BaseModel):
    """Paginated user list response."""
    
    items: List[UserResponse] = Field(
        ...,
        description="List of users for current page"
    )
    total: int = Field(
        ...,
        ge=0,
        description="Total number of users matching filter",
        examples=[100]
    )
    page: int = Field(
        ...,
        ge=1,
        description="Current page number (1-indexed)",
        examples=[1]
    )
    size: int = Field(
        ...,
        ge=1,
        le=100,
        description="Number of items per page",
        examples=[10]
    )
    pages: int = Field(
        ...,
        ge=1,
        description="Total number of pages",
        examples=[10]
    )
