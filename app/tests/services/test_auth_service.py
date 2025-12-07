import pytest
from jose import jwt, JWTError
from unittest.mock import patch, MagicMock
import logging
from fastapi import HTTPException
from datetime import timedelta

from app.services.auth_service import AuthService
from app.exceptions.base import UnauthorizedException, ValidationException
from app.core.config import settings
from app.core.security import create_access_token, create_refresh_token, verify_token, _get_verification_key
from app.models.user import UserRole
from app.services.password_service import PasswordService

logger = logging.getLogger(__name__)


def test_create_access_token(mock_db):
    """Test access token creation with all standard claims."""
    mock_user = MagicMock(
        id=1,
        email="test@example.com",
        full_name="Test User",
        role=UserRole.USER,
        is_active=True
    )
    auth_service = AuthService(mock_db)
    
    token = auth_service.create_access_token(mock_user)
    
    # Verify token using the correct key and algorithm
    verification_key = _get_verification_key()
    payload = verify_token(token)
    
    # Check standard JWT claims
    assert payload["sub"] == str(mock_user.id)
    assert payload["role"] == mock_user.role.value
    assert payload["iss"] == settings.JWT_ISSUER
    assert payload["aud"] == settings.JWT_AUDIENCE
    assert payload["type"] == "access"
    assert "exp" in payload
    assert "iat" in payload
    assert "jti" in payload
    
    # Check custom claims
    assert "permissions" in payload
    assert isinstance(payload["permissions"], list)
    assert payload["email"] == mock_user.email
    assert payload["is_active"] == mock_user.is_active
    assert payload["name"] == mock_user.full_name


def test_verify_token(mock_db):
    """Test token verification with real token generation."""
    auth_service = AuthService(mock_db)
    
    # Generate a real token
    token = create_access_token(
        subject=1,
        role=UserRole.USER,
        additional_claims={"email": "test@example.com"}
    )
    
    # Verify the token
    payload = auth_service.verify_token(token)
    
    # Check all claims
    assert payload["sub"] == "1"
    assert payload["role"] == UserRole.USER.value
    assert payload["iss"] == settings.JWT_ISSUER
    assert payload["aud"] == settings.JWT_AUDIENCE
    assert payload["type"] == "access"
    assert "permissions" in payload
    logger.info("Token verification test passed")


def test_verify_token_invalid(mock_db):
    """Test token verification with invalid token."""
    auth_service = AuthService(mock_db)
    
    with pytest.raises(UnauthorizedException) as exc_info:
        auth_service.verify_token("invalid_token")
    assert "Invalid token" in str(exc_info.value.detail)
    logger.info("Invalid token test passed")


def test_create_refresh_token(mock_db):
    """Test refresh token creation."""
    auth_service = AuthService(mock_db)
    
    mock_user = MagicMock(
        id=1,
        email="test@example.com",
        role=UserRole.USER,
        is_active=True
    )
    
    # Test create_tokens method
    access_token, refresh_token = auth_service.create_tokens(mock_user)
    
    # Verify both tokens
    access_payload = verify_token(access_token)
    refresh_payload = verify_token(refresh_token)
    
    # Check access token
    assert access_payload["sub"] == "1"
    assert access_payload["type"] == "access"
    assert "permissions" in access_payload
    
    # Check refresh token
    assert refresh_payload["sub"] == "1"
    assert refresh_payload["type"] == "refresh"
    assert "permissions" not in refresh_payload  # Refresh tokens don't have permissions
    logger.info("Refresh token test passed")


def test_refresh_access_token(mock_db):
    """Test refreshing access token using refresh token."""
    auth_service = AuthService(mock_db)
    
    mock_user = MagicMock(
        id=1,
        email="test@example.com",
        full_name="Test User",
        role=UserRole.USER,
        is_active=True
    )
    
    # Create initial tokens
    _, refresh_token = auth_service.create_tokens(mock_user)
    
    # Mock user service to return user
    auth_service.user_service.get = MagicMock(return_value=mock_user)
    
    # Refresh tokens
    new_access_token, new_refresh_token = auth_service.refresh_access_token(refresh_token)
    
    # Verify new tokens
    access_payload = verify_token(new_access_token)
    refresh_payload = verify_token(new_refresh_token)
    
    assert access_payload["sub"] == "1"
    assert access_payload["type"] == "access"
    assert refresh_payload["sub"] == "1"
    assert refresh_payload["type"] == "refresh"
    logger.info("Refresh access token test passed")


def test_authenticate_user(auth_service, mock_user_repository):
    logger.info("Testing authenticate user")
    password = "Test123!"
    hashed_password = PasswordService.get_password_hash(password)

    mock_user = MagicMock(
        id=1,
        email="test@example.com",
        full_name="Test User",
        role=UserRole.USER,
        is_active=True,
        hashed_password=hashed_password
    )

    auth_service.user_service.repository = mock_user_repository
    mock_user_repository.get_by_email.return_value = mock_user

    authenticated_user = auth_service.authenticate_user("test@example.com", password)
    assert authenticated_user.id == mock_user.id
    assert authenticated_user.email == mock_user.email
    assert authenticated_user.full_name == mock_user.full_name
    assert authenticated_user.role == mock_user.role
    assert authenticated_user.is_active == mock_user.is_active

    mock_user_repository.get_by_email.return_value = None
    with pytest.raises(UnauthorizedException) as exc_info:
        auth_service.authenticate_user("nonexistent@example.com", password)
    assert str(exc_info.value.detail) == "Incorrect email or password"

    mock_user_repository.get_by_email.return_value = mock_user
    with pytest.raises(UnauthorizedException) as exc_info:
        auth_service.authenticate_user("test@example.com", "wrongpassword")
    assert str(exc_info.value.detail) == "Incorrect email or password"
    logger.info("Authenticate user test passed") 