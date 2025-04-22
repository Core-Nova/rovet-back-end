from fastapi import FastAPI
from fastapi.testclient import TestClient
import pytest
from unittest.mock import patch, MagicMock
import logging

from app.middleware.auth_middleware import AuthMiddleware, AdminMiddleware
from app.core.config import settings
from app.models.user import UserRole
from app.api.v1.api import api_router
from app.main import app


USER_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwicm9sZSI6InVzZXIifQ.4Adcj3UFYzPUVaVF43FmMze6x7Yp4Yh4j3YwqXh5Yw"
ADMIN_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwicm9sZSI6IkFETUlOIn0.4Adcj3UFYzPUVaVF43FmMze6x7Yp4Yh4j3Yw"
INVALID_TOKEN = "invalid_token"


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
    headers = {"Authorization": f"Bearer {INVALID_TOKEN}"}
    response = client.get(f"{settings.API_V1_STR}/users/", headers=headers)
    assert response.status_code == 401


def test_protected_path_with_valid_token(client: TestClient, mock_auth_service):
    mock_auth_service.verify_token.return_value = {"sub": "1", "role": UserRole.USER}
    mock_auth_service.get_current_user.return_value = MagicMock(
        id=1,
        email="test@example.com",
        role=UserRole.USER,
        is_active=True
    )

    with patch("app.middleware.auth_middleware.AuthService", return_value=mock_auth_service):
        headers = {"Authorization": f"Bearer {USER_TOKEN}"}
        response = client.get(f"{settings.API_V1_STR}/users/", headers=headers)
        assert response.status_code == 403


def test_admin_path_with_normal_user(client: TestClient, mock_auth_service):
    mock_auth_service.verify_token.return_value = {"sub": "1", "role": UserRole.USER}
    mock_auth_service.get_current_user.return_value = MagicMock(
        id=1,
        email="test@example.com",
        role=UserRole.USER,
        is_active=True
    )

    with patch("app.middleware.auth_middleware.AuthService", return_value=mock_auth_service):
        headers = {"Authorization": f"Bearer {USER_TOKEN}"}
        response = client.get(f"{settings.API_V1_STR}/users/", headers=headers)
        assert response.status_code == 403


def test_admin_path_with_admin_user(client: TestClient, mock_auth_service):
    mock_auth_service.verify_token.return_value = {"sub": "1", "role": UserRole.ADMIN.value}
    mock_auth_service.get_current_user.return_value = MagicMock(
        id=1,
        email="admin@example.com",
        role=UserRole.ADMIN,
        is_active=True
    )

    with patch("app.middleware.auth_middleware.AuthService", return_value=mock_auth_service), \
         patch("app.services.auth_service.jwt.decode") as mock_decode, \
         patch("app.api.deps.AuthService", return_value=mock_auth_service):
            mock_decode.return_value = {"sub": "1", "role": UserRole.ADMIN.value}
            headers = {"Authorization": f"Bearer {ADMIN_TOKEN}"}
            response = client.get(f"{settings.API_V1_STR}/users/", headers=headers)
            assert response.status_code == 200