import pytest
from datetime import datetime, timedelta
from jose import jwt
from unittest.mock import patch, MagicMock
import logging
from fastapi import HTTPException

from app.services.auth_service import AuthService, ALGORITHM
from app.exceptions.base import UnauthorizedException
from app.core.config import settings
from app.models.user import UserRole
from app.services.password_service import PasswordService

logger = logging.getLogger(__name__)


def test_create_access_token(mock_db):
    mock_user = MagicMock(
        id=1,
        email="test@example.com",
        role=UserRole.USER,
        is_active=True
    )
    auth_service = AuthService(mock_db)
    
    token = auth_service.create_access_token(mock_user)
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
    
    assert payload["sub"] == str(mock_user.id)
    assert payload["role"] == mock_user.role.value
    assert "exp" in payload


def test_verify_token(mock_db):
    auth_service = AuthService(mock_db)
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwicm9sZSI6InVzZXIifQ.4Adcj3UFYzPUVaVF43FmMze6x7Yp4Yh4j3YwqXh5Yw"
    
    with patch("app.services.auth_service.jwt.decode") as mock_decode:
        mock_decode.return_value = {"sub": "1", "role": "user"}
        payload = auth_service.verify_token(token)
        assert payload["sub"] == "1"
        assert payload["role"] == "user"
        logger.info("Token verification test passed")


def test_verify_token_invalid(mock_db):
    auth_service = AuthService(mock_db)
    token = "invalid_token"
    
    with patch("app.services.auth_service.jwt.decode") as mock_decode:
        mock_decode.side_effect = jwt.InvalidTokenError("Invalid token: Not enough segments")
        with pytest.raises(HTTPException) as exc_info:
            auth_service.verify_token(token)
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid token: Not enough segments"
        logger.info("Invalid token test passed")


def test_authenticate_user(mock_db, mock_user_repository):
    auth_service = AuthService(mock_db)
    password = "TestPassword123!"
    mock_user = MagicMock(
        id=1,
        email="test@example.com",
        role=UserRole.USER,
        is_active=True,
        hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyDAZ1Qh0tXv6"  # Mock hashed password
    )
    
    # Configure mock repository
    mock_user_repository.get_by_email.return_value = mock_user
    
    # Test valid credentials
    with patch.object(PasswordService, 'verify_password', return_value=True):
        authenticated_user = auth_service.authenticate_user(mock_user.email, password)
        assert authenticated_user is not None
        assert authenticated_user == mock_user  # Compare the entire mock object
        logger.info("User authentication test passed")
    
    # Test invalid credentials
    with patch.object(PasswordService, 'verify_password', return_value=False):
        authenticated_user = auth_service.authenticate_user(mock_user.email, "wrong_password")
        assert authenticated_user is None
    
    # Test non-existent user
    mock_user_repository.get_by_email.return_value = None
    with pytest.raises(UnauthorizedException):
        auth_service.authenticate_user("nonexistent@example.com", password) 