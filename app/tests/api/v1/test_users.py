import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import logging
from fastapi import HTTPException

logger = logging.getLogger(__name__)

from app.core.config import settings
from app.models.user import User, UserRole
from app.api.v1.endpoints import users
from app.dto.user import UserFilter
from app.schemas.user import User, PaginatedUserResponse


@pytest.fixture(scope="function")
def mock_admin_user():
    """Create a mock admin user for testing"""
    return MagicMock(
        id=1,
        email="admin@example.com",
        full_name="Admin User",
        role=UserRole.ADMIN,
        is_active=True
    )


@pytest.fixture(scope="function")
def mock_normal_user():
    """Create a mock normal user for testing"""
    return MagicMock(
        id=2,
        email="user@example.com",
        full_name="Normal User",
        role=UserRole.USER,
        is_active=True
    )


@pytest.fixture(scope="function")
def mock_target_user():
    """Create a mock target user for testing update/delete operations"""
    return MagicMock(
        id=3,
        email="target@example.com",
        full_name="Target User",
        role=UserRole.USER,
        is_active=True
    )


@pytest.fixture(scope="function")
def mock_user_list():
    """Create a list of mock users for testing list operations"""
    return [
        MagicMock(
            id=1,
            email="user1@example.com",
            full_name="User One",
            role=UserRole.USER,
            is_active=True
        ),
        MagicMock(
            id=2,
            email="user2@example.com",
            full_name="User Two",
            role=UserRole.USER,
            is_active=True
        )
    ]


@pytest.fixture
def mock_auth_service_setup():
    """Setup mock auth service."""
    mock_service = MagicMock()
    mock_user = MagicMock(
        id=1,
        email="admin@example.com",
        full_name="Admin User",
        role=UserRole.ADMIN,
        is_active=True
    )
    mock_service.get_current_user.return_value = mock_user
    mock_service.verify_token.return_value = {
        "sub": "1",
        "role": "admin"
    }
    mock_service.user_service = MagicMock()
    mock_service.user_service.get.return_value = mock_user
    return mock_service


@pytest.fixture
def mock_user_repository_setup():
    """Setup mock user repository."""
    logger.info("Setting up mock user repository")
    mock_repo = MagicMock()
    mock_user = MagicMock(
        id=3,
        email="target@example.com",
        full_name="Target User",
        role=UserRole.USER,
        is_active=True
    )
    mock_repo.get_by_id.return_value = mock_user
    logger.info(f"Mock user repository configured with user: {mock_user.email} (ID: {mock_user.id})")
    return mock_repo


def test_get_all_users_unauthorized(client: TestClient):
    """Test get all users without authorization."""
    logger.info("Testing get all users without authorization")
    response = client.get(f"{settings.API_V1_STR}/users/")
    logger.debug(f"Get all users response: {response.status_code}")
    assert response.status_code == 401
    logger.info("Unauthorized access test passed")


def test_get_all_users_forbidden(client: TestClient, mock_auth_service_setup):
    """Test get all users with non-admin user."""
    logger.info("Testing get all users with non-admin user")
    mock_user = MagicMock(
        id=2,
        email="user@example.com",
        full_name="Normal User",
        role=UserRole.USER,
        is_active=True
    )
    logger.info(f"Setting up non-admin user: {mock_user.email} (ID: {mock_user.id})")
    mock_auth_service_setup.get_current_user.return_value = mock_user
    mock_auth_service_setup.verify_token.return_value = {
        "sub": "2",
        "role": "user"
    }

    mock_auth_service_setup.user_service.get.return_value = mock_user
    logger.info("Mock auth service configured with non-admin user")

    with patch("app.middleware.auth_middleware.AuthService", return_value=mock_auth_service_setup):
        headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIyIiwicm9sZSI6InVzZXIifQ.4Adcj3UFYzPUVaVF43FmMze6x7Yp4Yh4j3Yw"}
        response = client.get(f"{settings.API_V1_STR}/users/", headers=headers)
        logger.debug(f"Response status: {response.status_code}")
        logger.debug(f"Response body: {response.json()}")
        assert response.status_code == 403
        assert response.json()["detail"] == "Admin access required"
        logger.info("Non-admin access test passed")


def test_get_all_users_as_admin(client: TestClient, mock_auth_service_setup, mock_user_repository_setup):
    """Test get all users with admin user."""
    logger.info("Testing get all users with admin user")
    
    logger.info(f"Admin user from auth service: {mock_auth_service_setup.get_current_user.return_value.email} (ID: {mock_auth_service_setup.get_current_user.return_value.id})")
    logger.info(f"Target user from repository: {mock_user_repository_setup.get_by_id.return_value.email} (ID: {mock_user_repository_setup.get_by_id.return_value.id})")
    
    mock_user_repository_setup.get_filtered_users.return_value = ([mock_user_repository_setup.get_by_id.return_value], 1)
    logger.info("Mock repository configured to return filtered users")
    
    with patch("app.middleware.auth_middleware.AuthService", return_value=mock_auth_service_setup), \
         patch("app.api.v1.endpoints.users.UserRepository", return_value=mock_user_repository_setup), \
         patch("app.services.auth_service.jwt.decode") as mock_jwt_decode, \
         patch("app.services.auth_service.UserService") as mock_user_service:

        mock_user_service_instance = MagicMock()
        mock_user_service_instance.get.return_value = mock_auth_service_setup.get_current_user.return_value
        mock_user_service.return_value = mock_user_service_instance
        logger.info("Mock user service configured")
        
        mock_jwt_decode.return_value = {"sub": "1", "role": "admin"}
        headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIn0.4Adcj3UFYzPUVaVF43FmMze6x7Yp4Yh4j3Yw"}
        
        logger.info(f"Making request to {settings.API_V1_STR}/users/")
        logger.debug(f"Request headers: {headers}")
        
        response = client.get(f"{settings.API_V1_STR}/users/", headers=headers)
        logger.debug(f"Response status: {response.status_code}")
        logger.debug(f"Response body: {response.json()}")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["email"] == "target@example.com"
        logger.info("Get all users test passed")


def test_get_all_users_with_filters(client: TestClient, mock_auth_service_setup, mock_user_repository_setup):
    """Test get all users with filters."""
    logger.info("Testing get all users with filters")
    
    logger.info(f"Admin user from auth service: {mock_auth_service_setup.get_current_user.return_value.email} (ID: {mock_auth_service_setup.get_current_user.return_value.id})")
    logger.info(f"Target user from repository: {mock_user_repository_setup.get_by_id.return_value.email} (ID: {mock_user_repository_setup.get_by_id.return_value.id})")
    
    filtered_users = [mock_user_repository_setup.get_by_id.return_value]
    mock_user_repository_setup.get_filtered_users.return_value = (filtered_users, 1)
    logger.info("Mock repository configured to return filtered users")
    
    with patch("app.middleware.auth_middleware.AuthService", return_value=mock_auth_service_setup), \
         patch("app.api.v1.endpoints.users.UserRepository", return_value=mock_user_repository_setup), \
         patch("app.services.auth_service.jwt.decode") as mock_jwt_decode, \
         patch("app.services.auth_service.UserService") as mock_user_service:

        mock_user_service_instance = MagicMock()
        mock_user_service_instance.get.return_value = mock_auth_service_setup.get_current_user.return_value
        mock_user_service.return_value = mock_user_service_instance
        logger.info("Mock user service configured")
        
        mock_jwt_decode.return_value = {"sub": "1", "role": "admin"}
        headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIn0.4Adcj3UFYzPUVaVF43FmMze6x7Yp4Yh4j3Yw"}
        
        logger.info(f"Making request to {settings.API_V1_STR}/users/ with filters")
        logger.debug(f"Request headers: {headers}")
        logger.debug(f"Request params: email=target@example.com, role={UserRole.USER.value}")
        
        response = client.get(
            f"{settings.API_V1_STR}/users/",
            params={"email": "target@example.com", "role": UserRole.USER.value},
            headers=headers
        )
        logger.debug(f"Response status: {response.status_code}")
        logger.debug(f"Response body: {response.json()}")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) == 1
        assert data["items"][0]["email"] == "target@example.com"
        logger.info("Filtered users test passed")


def test_get_user_by_id(client: TestClient, mock_auth_service_setup, mock_user_repository_setup):
    """Test get user by ID."""
    logger.info("Testing get user by ID")
    
    logger.info(f"Admin user from auth service: {mock_auth_service_setup.get_current_user.return_value.email} (ID: {mock_auth_service_setup.get_current_user.return_value.id})")
    logger.info(f"Target user from repository: {mock_user_repository_setup.get_by_id.return_value.email} (ID: {mock_user_repository_setup.get_by_id.return_value.id})")
    
    with patch("app.middleware.auth_middleware.AuthService", return_value=mock_auth_service_setup), \
         patch("app.api.v1.endpoints.users.UserRepository", return_value=mock_user_repository_setup), \
         patch("app.services.auth_service.jwt.decode") as mock_jwt_decode, \
         patch("app.services.auth_service.UserService") as mock_user_service:

        mock_user_service_instance = MagicMock()
        mock_user_service_instance.get.return_value = mock_auth_service_setup.get_current_user.return_value
        mock_user_service.return_value = mock_user_service_instance
        logger.info("Mock user service configured")
        
        mock_jwt_decode.return_value = {"sub": "1", "role": "admin"}
        headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIn0.4Adcj3UFYzPUVaVF43FmMze6x7Yp4Yh4j3Yw"}
        
        logger.info(f"Making request to {settings.API_V1_STR}/users/3")
        logger.debug(f"Request headers: {headers}")
        
        response = client.get(f"{settings.API_V1_STR}/users/3", headers=headers)
        logger.debug(f"Response status: {response.status_code}")
        logger.debug(f"Response body: {response.json()}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "target@example.com"
        logger.info("Get user by ID test passed")


def test_update_user(client: TestClient, mock_auth_service_setup, mock_user_repository_setup):
    """Test update user."""
    logger.info("Testing update user")
    
    logger.info(f"Admin user from auth service: {mock_auth_service_setup.get_current_user.return_value.email} (ID: {mock_auth_service_setup.get_current_user.return_value.id})")
    logger.info(f"Target user from repository: {mock_user_repository_setup.get_by_id.return_value.email} (ID: {mock_user_repository_setup.get_by_id.return_value.id})")
    
    updated_user = MagicMock(
        id=3,
        email="updated@example.com",
        full_name="Updated User",
        role=UserRole.USER,
        is_active=True
    )
    mock_user_repository_setup.update.return_value = updated_user
    logger.info(f"Mock repository configured to return updated user: {updated_user.email}")
    
    with patch("app.middleware.auth_middleware.AuthService", return_value=mock_auth_service_setup), \
         patch("app.api.v1.endpoints.users.UserRepository", return_value=mock_user_repository_setup), \
         patch("app.services.auth_service.jwt.decode") as mock_jwt_decode, \
         patch("app.services.auth_service.UserService") as mock_user_service:

        mock_user_service_instance = MagicMock()
        mock_user_service_instance.get.return_value = mock_auth_service_setup.get_current_user.return_value
        mock_user_service.return_value = mock_user_service_instance
        logger.info("Mock user service configured")
        
        mock_jwt_decode.return_value = {"sub": "1", "role": "admin"}
        headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIn0.4Adcj3UFYzPUVaVF43FmMze6x7Yp4Yh4j3Yw"}
        
        update_data = {
            "email": "updated@example.com",
            "full_name": "Updated User"
        }
        logger.info(f"Making request to {settings.API_V1_STR}/users/3")
        logger.debug(f"Request headers: {headers}")
        logger.debug(f"Request body: {update_data}")
        
        response = client.put(
            f"{settings.API_V1_STR}/users/3",
            json=update_data,
            headers=headers
        )
        logger.debug(f"Response status: {response.status_code}")
        logger.debug(f"Response body: {response.json()}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "updated@example.com"
        assert data["full_name"] == "Updated User"
        logger.info("Update user test passed")


def test_delete_user(client: TestClient, mock_auth_service_setup, mock_user_repository_setup):
    """Test delete user."""
    logger.info("Testing delete user")
    
    logger.info(f"Admin user from auth service: {mock_auth_service_setup.get_current_user.return_value.email} (ID: {mock_auth_service_setup.get_current_user.return_value.id})")
    logger.info(f"Target user from repository: {mock_user_repository_setup.get_by_id.return_value.email} (ID: {mock_user_repository_setup.get_by_id.return_value.id})")
    
    with patch("app.middleware.auth_middleware.AuthService", return_value=mock_auth_service_setup), \
         patch("app.api.v1.endpoints.users.UserRepository", return_value=mock_user_repository_setup), \
         patch("app.services.auth_service.jwt.decode") as mock_jwt_decode, \
         patch("app.services.auth_service.UserService") as mock_user_service:
        
        mock_user_service_instance = MagicMock()
        mock_user_service_instance.get.return_value = mock_auth_service_setup.get_current_user.return_value
        mock_user_service.return_value = mock_user_service_instance
        logger.info("Mock user service configured")
        
        mock_jwt_decode.return_value = {"sub": "1", "role": "admin"}
        headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwicm9sZSI6ImFkbWluIn0.4Adcj3UFYzPUVaVF43FmMze6x7Yp4Yh4j3Yw"}
        
        logger.info(f"Making request to {settings.API_V1_STR}/users/3")
        logger.debug(f"Request headers: {headers}")
        
        response = client.delete(f"{settings.API_V1_STR}/users/3", headers=headers)
        logger.debug(f"Response status: {response.status_code}")
        
        assert response.status_code == 204
        logger.info("Delete user test passed") 