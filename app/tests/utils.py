from typing import Dict, Optional
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import get_password_hash
from app.models.user import User, UserRole


def create_test_user(
    db: Session,
    *,
    email: str = "test@example.com",
    password: str = "Test123!",
    full_name: str = "Test User",
    role: UserRole = UserRole.USER,
    is_active: bool = True
) -> User:
    user = User(
        email=email,
        hashed_password=get_password_hash(password),
        full_name=full_name,
        role=role,
        is_active=is_active
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def user_authentication_headers(
    *, client: TestClient, email: str, password: str
) -> Dict[str, str]:
    data = {"email": email, "password": password}
    r = client.post(f"{settings.API_V1_STR}/auth/login", json=data)
    response = r.json()
    if "access_token" not in response:
        raise ValueError(f"Login failed: {response}")
    auth_token = response["access_token"]
    return {"Authorization": f"Bearer {auth_token}"}


def create_test_admin(
    db: Session,
    *,
    email: str = "admin@example.com",
    password: str = "Admin123!",
    full_name: str = "Admin User",
    is_active: bool = True
) -> User:
    return create_test_user(
        db, 
        email=email, 
        password=password, 
        full_name=full_name, 
        role=UserRole.ADMIN,
        is_active=is_active
    ) 