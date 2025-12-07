from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import logging
from fastapi import HTTPException

logger = logging.getLogger(__name__)

from app.core.config import settings
from app.core.security import create_access_token
from app.models.user import UserRole



def test_register_user(client: TestClient, mock_user_repository):
    logger.info("Testing user registration")
    data = {
        "email": "test@example.com",
        "password": "Test123!",
        "full_name": "Test User"
    }
    response = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json=data,
    )
    logger.debug(f"Registration response: {response.status_code}")
    assert response.status_code == 409
    assert response.json()["detail"] == "The user with this email already exists in the system"


def test_register_existing_user(client: TestClient, mock_user_repository):
    logger.info("Testing registration of existing user")
    mock_user_repository.get_by_email.return_value = MagicMock(
        id=1,
        email="test@example.com",
        full_name="Test User",
        role=UserRole.USER,
        is_active=True
    )
    
    data = {
        "email": "test@example.com",
        "password": "Test123!",
        "full_name": "Test User"
    }
    response = client.post(
        f"{settings.API_V1_STR}/auth/register",
        json=data,
    )
    logger.debug(f"Registration response: {response.status_code}")
    assert response.status_code == 409
    assert response.json()["detail"] == "The user with this email already exists in the system"


def test_login_user(client: TestClient, mock_auth_service):
    """Test user login returns both access and refresh tokens."""
    logger.info("Testing user login")
    
    # Mock create_tokens to return real tokens
    from app.core.security import create_access_token, create_refresh_token
    mock_user = MagicMock(
        id=1,
        email="test@example.com",
        full_name="Test User",
        role=UserRole.USER,
        is_active=True
    )
    mock_auth_service.authenticate_user.return_value = mock_user
    mock_auth_service.create_tokens.return_value = (
        create_access_token(subject=1, role=UserRole.USER),
        create_refresh_token(subject=1)
    )
    
    with patch("app.controllers.auth_controller.AuthService", return_value=mock_auth_service):
        data = {
            "email": "test@example.com",
            "password": "Test123!",
        }
        response = client.post(f"{settings.API_V1_STR}/auth/login", json=data)
        logger.debug(f"Login response: {response.status_code}")
        assert response.status_code == 200
        content = response.json()
        assert "access_token" in content
        assert "refresh_token" in content
        assert content["token_type"] == "bearer"
        assert "expires_in" in content
        assert content["expires_in"] == settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        logger.info("User login test passed")


def test_login_incorrect_password(client: TestClient, mock_auth_service):
    logger.info("Testing login with incorrect password")
    mock_auth_service.authenticate_user.side_effect = Exception("Invalid credentials")
    
    with patch("app.api.v1.endpoints.auth.AuthService", return_value=mock_auth_service):
        data = {
            "email": "test@example.com",
            "password": "Wrong123!",
        }
        response = client.post(f"{settings.API_V1_STR}/auth/login", json=data)
        logger.debug(f"Login response: {response.status_code}")
        assert response.status_code == 401
        logger.info("Incorrect password login test passed")


def test_get_current_user(client: TestClient, mock_auth_service):
    """Test get current user with real token."""
    logger.info("Testing get current user")
    mock_user = MagicMock(
        id=1,
        email="test@example.com",
        full_name="Test User",
        role=UserRole.USER,
        is_active=True
    )
    mock_auth_service.get_current_user.return_value = mock_user
    
    # Generate a real token
    token = create_access_token(subject=1, role=UserRole.USER)
    
    with patch("app.middleware.auth_middleware.AuthService", return_value=mock_auth_service), \
         patch("app.controllers.auth_controller.AuthService", return_value=mock_auth_service):
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get(f"{settings.API_V1_STR}/auth/me", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["email"] == "test@example.com"
        assert data["role"] == UserRole.USER.value
        assert data["is_active"] is True
        logger.info("Get current user test passed")


def test_refresh_token(client: TestClient, mock_auth_service):
    """Test refresh token endpoint."""
    logger.info("Testing refresh token")
    
    from app.core.security import create_access_token, create_refresh_token
    
    mock_user = MagicMock(
        id=1,
        email="test@example.com",
        full_name="Test User",
        role=UserRole.USER,
        is_active=True
    )
    
    refresh_token = create_refresh_token(subject=1)
    new_access_token = create_access_token(subject=1, role=UserRole.USER)
    new_refresh_token = create_refresh_token(subject=1)
    
    mock_auth_service.refresh_access_token.return_value = (new_access_token, new_refresh_token)
    
    with patch("app.controllers.auth_controller.AuthService", return_value=mock_auth_service):
        data = {"refresh_token": refresh_token}
        response = client.post(f"{settings.API_V1_STR}/auth/refresh", json=data)
        logger.debug(f"Refresh response: {response.status_code}")
        assert response.status_code == 200
        content = response.json()
        assert "access_token" in content
        assert "refresh_token" in content
        assert content["token_type"] == "bearer"
        assert "expires_in" in content
        logger.info("Refresh token test passed")


def test_get_current_user_invalid_token(client: TestClient, mock_auth_service):
    logger.info("Testing get current user with invalid token")
    mock_auth_service.verify_token.side_effect = HTTPException(
        status_code=401,
        detail="Invalid token: Not enough segments"
    )
    
    with patch("app.middleware.auth_middleware.AuthService", return_value=mock_auth_service):
        headers = {"Authorization": "Bearer invalid_token"}
        response = client.get(f"{settings.API_V1_STR}/auth/me", headers=headers)
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid token: Not enough segments"
        logger.info("Invalid token test passed")


def test_get_current_user_no_token(client: TestClient, mock_auth_service):
    logger.info("Testing get current user without token")
    mock_auth_service.verify_token.side_effect = HTTPException(
        status_code=401,
        detail="Missing or invalid authentication token"
    )
    
    with patch("app.middleware.auth_middleware.AuthService", return_value=mock_auth_service):
        response = client.get(f"{settings.API_V1_STR}/auth/me")
        assert response.status_code == 401
        assert response.json()["detail"] == "Missing or invalid authentication token"
        logger.info("No token test passed") 