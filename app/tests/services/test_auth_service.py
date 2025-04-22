import pytest
from jose import jwt, JWTError
from unittest.mock import patch, MagicMock
import logging
from fastapi import HTTPException

from app.services.auth_service import AuthService, ALGORITHM
from app.exceptions.base import UnauthorizedException, ValidationException
from app.core.config import settings
from app.models.user import UserRole
from app.services.password_service import PasswordService

logger = logging.getLogger(__name__)

VALID_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwicm9sZSI6InVzZXIifQ.4Adcj3UFYzPUVaVF43FmMze6x7Yp4Yh4j3YwqXh5Yw"


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
    
    with patch("app.services.auth_service.jwt.decode") as mock_decode:
        mock_decode.return_value = {"sub": "1", "role": "user"}
        payload = auth_service.verify_token(VALID_TOKEN)
        assert payload["sub"] == "1"
        assert payload["role"] == "user"
        logger.info("Token verification test passed")


def test_verify_token_invalid(mock_db):
    auth_service = AuthService(mock_db)
    
    with patch("app.services.auth_service.jwt.decode") as mock_decode:
        mock_decode.side_effect = JWTError("Not enough segment")
        with pytest.raises(HTTPException) as exc_info:
            auth_service.verify_token("invalid_token")
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Invalid token: Not enough segment"
        logger.info("Invalid token test passed")


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