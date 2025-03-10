from pydantic import BaseModel, EmailStr
from app.models.user import UserRole


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    sub: int
    role: UserRole
    exp: int
