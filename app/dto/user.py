from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(UserBase):
    password: Optional[str] = None


class UserResponse(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserFilter(BaseModel):
    email: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class PaginatedUserResponse(BaseModel):
    items: List[UserResponse]
    total: int
    page: int
    size: int
    pages: int 