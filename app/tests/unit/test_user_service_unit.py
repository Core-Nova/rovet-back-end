"""
Unit tests for UserService.

These tests are FAST and ISOLATED:
- Mock all dependencies (repository, password service)
- Test business logic only
- No database operations
- Run in <1ms each
"""

import pytest
from unittest.mock import MagicMock
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository
from app.services.password_service import PasswordService
from app.exceptions.base import ConflictException, NotFoundException
from app.tests.factories import UserFactory, TestData
from app.models.user import User, UserRole


@pytest.mark.unit
class TestUserServiceCreate:
    """Test UserService.create_user method."""
    
    def test_create_user_success(self, mock_user_repository, mock_password_service):
        """Test successful user creation with valid data."""
        # Arrange
        service = UserService(mock_user_repository, mock_password_service)
        user_data = UserFactory.build_create_dto()
        
        mock_user_repository.get_by_email.return_value = None  # Email doesn't exist
        mock_password_service.get_password_hash.return_value = "hashed_password"
        mock_user_repository.create_with_password.return_value = MagicMock(
            id=1,
            email=user_data.email,
            full_name=user_data.full_name
        )
        
        # Act
        result = service.create_user(user_data)
        
        # Assert
        assert result.id == 1
        assert result.email == user_data.email
        mock_user_repository.get_by_email.assert_called_once_with(email=user_data.email)
        mock_password_service.validate_password.assert_called_once_with(user_data.password)
        mock_password_service.get_password_hash.assert_called_once_with(user_data.password)
        mock_user_repository.create_with_password.assert_called_once()
    
    def test_create_user_duplicate_email_raises_conflict(
        self,
        mock_user_repository,
        mock_password_service
    ):
        """Test that creating user with existing email raises ConflictException."""
        # Arrange
        service = UserService(mock_user_repository, mock_password_service)
        user_data = UserFactory.build_create_dto()
        
        # Email already exists
        mock_user_repository.get_by_email.return_value = MagicMock(
            email=user_data.email
        )
        
        # Act & Assert
        with pytest.raises(ConflictException) as exc_info:
            service.create_user(user_data)
        
        assert "email already exists" in str(exc_info.value.detail).lower()
        mock_password_service.validate_password.assert_not_called()
        mock_user_repository.create_with_password.assert_not_called()
    
    def test_create_user_validates_password(
        self,
        mock_user_repository,
        mock_password_service
    ):
        """Test that password validation is called."""
        # Arrange
        service = UserService(mock_user_repository, mock_password_service)
        user_data = UserFactory.build_create_dto()
        mock_user_repository.get_by_email.return_value = None
        
        # Act
        service.create_user(user_data)
        
        # Assert
        mock_password_service.validate_password.assert_called_once_with(
            user_data.password
        )


@pytest.mark.unit
class TestUserServiceAuthenticate:
    """Test UserService.authenticate method."""
    
    def test_authenticate_success(self, mock_user_repository, mock_password_service):
        """Test successful authentication with valid credentials."""
        # Arrange
        service = UserService(mock_user_repository, mock_password_service)
        email = "test@example.com"
        password = "TestPass123!"
        
        mock_user = MagicMock(
            id=1,
            email=email,
            hashed_password="hashed_password"
        )
        mock_user_repository.get_by_email.return_value = mock_user
        mock_password_service.verify_password.return_value = True
        
        # Act
        result = service.authenticate(email, password)
        
        # Assert
        assert result == mock_user
        mock_user_repository.get_by_email.assert_called_once_with(email=email)
        mock_password_service.verify_password.assert_called_once_with(
            password,
            mock_user.hashed_password
        )
    
    def test_authenticate_user_not_found_returns_none(
        self,
        mock_user_repository,
        mock_password_service
    ):
        """Test authentication with non-existent email returns None."""
        # Arrange
        service = UserService(mock_user_repository, mock_password_service)
        mock_user_repository.get_by_email.return_value = None
        
        # Act
        result = service.authenticate("nonexistent@example.com", "password")
        
        # Assert
        assert result is None
        mock_password_service.verify_password.assert_not_called()
    
    def test_authenticate_wrong_password_returns_none(
        self,
        mock_user_repository,
        mock_password_service
    ):
        """Test authentication with wrong password returns None."""
        # Arrange
        service = UserService(mock_user_repository, mock_password_service)
        mock_user = MagicMock(hashed_password="hashed_password")
        mock_user_repository.get_by_email.return_value = mock_user
        mock_password_service.verify_password.return_value = False  # Wrong password
        
        # Act
        result = service.authenticate("test@example.com", "wrong_password")
        
        # Assert
        assert result is None


@pytest.mark.unit
class TestUserServiceUpdate:
    """Test UserService.update_user method."""
    
    def test_update_user_success(self, mock_user_repository, mock_password_service):
        """Test successful user update."""
        # Arrange
        service = UserService(mock_user_repository, mock_password_service)
        user_id = 1
        
        from app.dto.user import UserUpdate
        update_data = UserUpdate(
            email="newemail@example.com",
            full_name="New Name"
        )
        
        mock_user = MagicMock(id=user_id, email="old@example.com")
        mock_user_repository.get.return_value = mock_user
        mock_user_repository.get_by_email.return_value = None  # New email doesn't exist
        
        # Act
        result = service.update_user(user_id, update_data)
        
        # Assert
        assert result == mock_user
        mock_user_repository.db.commit.assert_called_once()
        mock_user_repository.db.refresh.assert_called_once_with(mock_user)
    
    def test_update_user_not_found_raises_exception(
        self,
        mock_user_repository,
        mock_password_service
    ):
        """Test updating non-existent user raises NotFoundException."""
        # Arrange
        service = UserService(mock_user_repository, mock_password_service)
        mock_user_repository.get.return_value = None
        
        from app.dto.user import UserUpdate
        update_data = UserUpdate(email="new@example.com")
        
        # Act & Assert
        with pytest.raises(NotFoundException):
            service.update_user(999, update_data)
    
    def test_update_email_to_existing_raises_conflict(
        self,
        mock_user_repository,
        mock_password_service
    ):
        """Test updating to existing email raises ConflictException."""
        # Arrange
        service = UserService(mock_user_repository, mock_password_service)
        user_id = 1
        
        from app.dto.user import UserUpdate
        update_data = UserUpdate(email="existing@example.com")
        
        mock_user = MagicMock(id=user_id, email="old@example.com")
        mock_user_repository.get.return_value = mock_user
        mock_user_repository.get_by_email.return_value = MagicMock()  # Email exists
        
        # Act & Assert
        with pytest.raises(ConflictException):
            service.update_user(user_id, update_data)


@pytest.mark.unit
def test_get_by_email(mock_user_repository, mock_password_service):
    """Test getting user by email."""
    # Arrange
    service = UserService(mock_user_repository, mock_password_service)
    email = "test@example.com"
    mock_user = MagicMock(email=email)
    mock_user_repository.get_by_email.return_value = mock_user
    
    # Act
    result = service.get_by_email(email)
    
    # Assert
    assert result == mock_user
    mock_user_repository.get_by_email.assert_called_once_with(email=email)


@pytest.mark.unit
def test_get_filtered_users(mock_user_repository, mock_password_service):
    """Test getting filtered users with pagination."""
    # Arrange
    service = UserService(mock_user_repository, mock_password_service)
    
    from app.dto.user import UserFilter
    filters = UserFilter(email="test", is_active=True)
    
    mock_users = [MagicMock(id=i) for i in range(5)]
    mock_user_repository.get_filtered_users.return_value = (mock_users, 15)  # 5 users, 15 total
    
    # Act
    result = service.get_filtered_users(filters, page=1, size=5)
    
    # Assert
    assert len(result.items) == 5
    assert result.total == 15
    assert result.page == 1
    assert result.size == 5
    assert result.pages == 3  # 15 / 5 = 3 pages
    mock_user_repository.get_filtered_users.assert_called_once()

