"""Tests for permission-based access control."""

from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import logging

logger = logging.getLogger(__name__)

from app.core.config import settings
from app.core.security import create_access_token
from app.models.user import UserRole
from app.tests.utils import create_test_token


def test_permission_checking(client: TestClient):
    """Test that tokens include permissions."""
    # Generate token for admin user
    token = create_access_token(subject=1, role=UserRole.ADMIN)
    
    # Verify token contains permissions
    from app.core.security import verify_token
    payload = verify_token(token)
    
    assert "permissions" in payload
    assert isinstance(payload["permissions"], list)
    assert len(payload["permissions"]) > 0
    assert "admin:access" in payload["permissions"]
    logger.info("Permission checking test passed")


def test_user_permissions(client: TestClient):
    """Test that regular users have correct permissions."""
    # Generate token for regular user
    token = create_access_token(subject=2, role=UserRole.USER)
    
    # Verify token contains user permissions
    from app.core.security import verify_token
    payload = verify_token(token)
    
    assert "permissions" in payload
    assert "users:read:own" in payload["permissions"]
    assert "admin:access" not in payload["permissions"]
    logger.info("User permissions test passed")


def test_admin_permissions(client: TestClient):
    """Test that admin users have correct permissions."""
    # Generate token for admin user
    token = create_access_token(subject=1, role=UserRole.ADMIN)
    
    # Verify token contains admin permissions
    from app.core.security import verify_token
    payload = verify_token(token)
    
    assert "permissions" in payload
    assert "users:read" in payload["permissions"]
    assert "users:write" in payload["permissions"]
    assert "users:delete" in payload["permissions"]
    assert "admin:access" in payload["permissions"]
    logger.info("Admin permissions test passed")

