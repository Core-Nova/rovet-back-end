from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
from unittest.mock import patch, MagicMock
import logging

from app.middleware.auth_middleware import AuthMiddleware, AdminMiddleware
from app.core.config import settings
from app.core.security import create_access_token
from app.models.user import UserRole
from app.api.v1.api import api_router
from app.main import app


def create_test_app():
    app = FastAPI()
    app.add_middleware(AuthMiddleware)
    app.add_middleware(AdminMiddleware)
    
    app.include_router(api_router, prefix=settings.API_V1_STR)
    
    @app.get("/test-auth")
    def test_auth():
        return {"message": "authenticated"}
    
    @app.get(f"{settings.API_V1_STR}/users/test-admin")
    def test_admin():
        return {"message": "admin only"}
    
    return app


@pytest.fixture
def client():
    return TestClient(app)


def test_public_paths(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200

    response = client.get(f"{settings.API_V1_STR}/health")
    assert response.status_code == 200


def test_protected_path_without_token(client: TestClient):
    response = client.get(f"{settings.API_V1_STR}/users/")
    assert response.status_code == 401


def test_protected_path_with_invalid_token(client: TestClient):
    """Test protected path with invalid token."""
    headers = {"Authorization": "Bearer invalid_token"}
    response = client.get(f"{settings.API_V1_STR}/users/", headers=headers)
    assert response.status_code == 401


def test_protected_path_with_valid_token(client: TestClient, mock_auth_service):
    """Test protected path with valid user token."""
    # Generate a real token
    token = create_access_token(subject=1, role=UserRole.USER)
    
    mock_auth_service.verify_token.return_value = {
        "sub": "1", 
        "role": UserRole.USER.value,
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "type": "access"
    }
    mock_auth_service.get_current_user.return_value = MagicMock(
        id=1,
        email="test@example.com",
        role=UserRole.USER,
        is_active=True
    )

    with patch("app.middleware.auth_middleware.AuthService", return_value=mock_auth_service):
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get(f"{settings.API_V1_STR}/users/", headers=headers)
        assert response.status_code == 403


def test_admin_path_with_normal_user(client: TestClient, mock_auth_service):
    """Test admin path with normal user token."""
    # Generate a real token
    token = create_access_token(subject=1, role=UserRole.USER)
    
    mock_auth_service.verify_token.return_value = {
        "sub": "1", 
        "role": UserRole.USER.value,
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "type": "access"
    }
    mock_auth_service.get_current_user.return_value = MagicMock(
        id=1,
        email="test@example.com",
        role=UserRole.USER,
        is_active=True
    )

    with patch("app.middleware.auth_middleware.AuthService", return_value=mock_auth_service):
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get(f"{settings.API_V1_STR}/users/", headers=headers)
        assert response.status_code == 403


def test_admin_path_with_admin_user(client: TestClient, mock_auth_service):
    """Test admin path with admin user token."""
    # Generate a real admin token
    token = create_access_token(subject=1, role=UserRole.ADMIN)
    
    mock_auth_service.verify_token.return_value = {
        "sub": "1", 
        "role": UserRole.ADMIN.value,
        "iss": settings.JWT_ISSUER,
        "aud": settings.JWT_AUDIENCE,
        "type": "access"
    }
    mock_auth_service.get_current_user.return_value = MagicMock(
        id=1,
        email="admin@example.com",
        role=UserRole.ADMIN,
        is_active=True
    )

    with patch("app.middleware.auth_middleware.AuthService", return_value=mock_auth_service), \
         patch("app.core.security.verify_token") as mock_verify, \
         patch("app.api.deps.AuthService", return_value=mock_auth_service):
            from app.core.security import verify_token as real_verify
            mock_verify.return_value = real_verify(token)
            headers = {"Authorization": f"Bearer {token}"}
            response = client.get(f"{settings.API_V1_STR}/users/", headers=headers)
            assert response.status_code == 200