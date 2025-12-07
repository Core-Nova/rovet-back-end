"""Integration tests for authentication flows using real database."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
import logging

logger = logging.getLogger(__name__)

from app.core.config import settings
from app.core.security import verify_token
from app.models.user import UserRole
from app.tests.utils import create_test_user, create_test_admin, create_test_token

# Note: These tests use the real database fixture from conftest.py


def test_full_login_flow(db: Session, client: TestClient):
    """Test complete login flow with real database."""
    logger.info("Testing full login flow")
    
    # Create a real user in the database
    user = create_test_user(
        db,
        email="integration@test.com",
        password="Test123!",
        full_name="Integration Test User"
    )
    
    # Test login
    login_data = {
        "email": "integration@test.com",
        "password": "Test123!"
    }
    response = client.post(f"{settings.API_V1_STR}/auth/login", json=login_data)
    
    assert response.status_code == 200
    data = response.json()
    
    # Verify response structure
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert "expires_in" in data
    
    # Verify tokens are valid
    access_token = data["access_token"]
    refresh_token = data["refresh_token"]
    
    access_payload = verify_token(access_token)
    refresh_payload = verify_token(refresh_token)
    
    # Check access token
    assert access_payload["sub"] == str(user.id)
    assert access_payload["role"] == UserRole.USER.value
    assert access_payload["type"] == "access"
    assert "permissions" in access_payload
    
    # Check refresh token
    assert refresh_payload["sub"] == str(user.id)
    assert refresh_payload["type"] == "refresh"
    
    logger.info("Full login flow test passed")


def test_token_refresh_flow(db: Session, client: TestClient):
    """Test complete token refresh flow."""
    logger.info("Testing token refresh flow")
    
    # Create a real user
    user = create_test_user(
        db,
        email="refresh@test.com",
        password="Test123!",
        full_name="Refresh Test User"
    )
    
    # Login to get tokens
    login_data = {
        "email": "refresh@test.com",
        "password": "Test123!"
    }
    login_response = client.post(f"{settings.API_V1_STR}/auth/login", json=login_data)
    assert login_response.status_code == 200
    
    refresh_token = login_response.json()["refresh_token"]
    
    # Refresh tokens
    refresh_data = {"refresh_token": refresh_token}
    refresh_response = client.post(f"{settings.API_V1_STR}/auth/refresh", json=refresh_data)
    
    assert refresh_response.status_code == 200
    new_data = refresh_response.json()
    
    # Verify new tokens
    assert "access_token" in new_data
    assert "refresh_token" in new_data
    
    new_access_payload = verify_token(new_data["access_token"])
    assert new_access_payload["sub"] == str(user.id)
    assert new_access_payload["type"] == "access"
    
    logger.info("Token refresh flow test passed")


def test_authenticated_request_flow(db: Session, client: TestClient):
    """Test making authenticated requests with token."""
    logger.info("Testing authenticated request flow")
    
    # Create admin user
    admin = create_test_admin(
        db,
        email="admin@test.com",
        password="Admin123!"
    )
    
    # Login
    login_data = {
        "email": "admin@test.com",
        "password": "Admin123!"
    }
    login_response = client.post(f"{settings.API_V1_STR}/auth/login", json=login_data)
    assert login_response.status_code == 200
    
    access_token = login_response.json()["access_token"]
    
    # Make authenticated request
    headers = {"Authorization": f"Bearer {access_token}"}
    response = client.get(f"{settings.API_V1_STR}/users/", headers=headers)
    
    # Should succeed for admin
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    
    logger.info("Authenticated request flow test passed")

