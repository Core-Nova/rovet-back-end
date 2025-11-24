"""
Integration tests for UserService.

These tests use REAL services and REAL database:
- Real UserRepository with test database
- Real PasswordService
- Tests actual integration between components
- Slower than unit tests (~10-100ms each)
- Tests database constraints, transactions, etc.
"""

import pytest
from app.exceptions.base import ConflictException, NotFoundException
from app.tests.factories import UserFactory, TestData


@pytest.mark.integration
class TestUserServiceIntegration:
    """Integration tests for UserService with real database."""
    
    def test_create_user_saves_to_database(self, user_service, db):
        """Test that creating user actually saves to database."""
        # Arrange
        user_data = UserFactory.build_create_dto(email="john@example.com")
        
        # Act
        created_user = user_service.create_user(user_data)
        
        # Assert - Check user was created
        assert created_user.id is not None
        assert created_user.email == "john@example.com"
        
        # Verify password was hashed (not plaintext)
        assert created_user.hashed_password != user_data.password
        assert len(created_user.hashed_password) > 20
        
        # Verify user exists in database
        db_user = db.query(from app.models.user import User).filter_by(
            email="john@example.com"
        ).first()
        assert db_user is not None
        assert db_user.id == created_user.id
    
    def test_create_duplicate_email_enforces_constraint(self, user_service):
        """Test database enforces unique email constraint."""
        # Arrange
        user_data = UserFactory.build_create_dto(email="duplicate@example.com")
        
        # Act - Create first user (should succeed)
        user1 = user_service.create_user(user_data)
        assert user1.id is not None
        
        # Act & Assert - Create second user with same email (should fail)
        with pytest.raises(ConflictException) as exc_info:
            user_service.create_user(user_data)
        
        assert "already exists" in str(exc_info.value.detail).lower()
    
    def test_authenticate_with_real_password_hashing(self, user_service):
        """Test authentication with real password hashing."""
        # Arrange - Create user
        password = "SecurePass123!"
        user_data = UserFactory.build_create_dto(
            email="auth@example.com",
            password=password
        )
        created_user = user_service.create_user(user_data)
        
        # Act & Assert - Authenticate with correct password
        authenticated = user_service.authenticate("auth@example.com", password)
        assert authenticated is not None
        assert authenticated.id == created_user.id
        
        # Assert - Wrong password fails
        assert user_service.authenticate("auth@example.com", "wrong") is None
        
        # Assert - Non-existent user fails
        assert user_service.authenticate("nonexistent@example.com", password) is None
    
    def test_update_user_persists_changes(self, user_service, db):
        """Test that updating user persists to database."""
        # Arrange - Create user
        user = UserFactory.create(user_service, email="update@example.com")
        original_id = user.id
        
        from app.dto.user import UserUpdate
        update_data = UserUpdate(
            email="newemail@example.com",
            full_name="New Name"
        )
        
        # Act - Update user
        updated_user = user_service.update_user(user.id, update_data)
        
        # Assert - Changes applied
        assert updated_user.id == original_id
        assert updated_user.email == "newemail@example.com"
        assert updated_user.full_name == "New Name"
        
        # Verify changes persisted to database
        db.refresh(updated_user)
        assert updated_user.email == "newemail@example.com"
    
    def test_update_password_with_real_hashing(self, user_service):
        """Test password update with real hashing and authentication."""
        # Arrange - Create user
        old_password = "OldPass123!"
        user = UserFactory.create(user_service, password=old_password)
        
        # Verify old password works
        assert user_service.authenticate(user.email, old_password) is not None
        
        # Act - Update password
        from app.dto.user import UserUpdate
        new_password = "NewPass456!"
        update_data = UserUpdate(password=new_password)
        user_service.update_user(user.id, update_data)
        
        # Assert - Old password doesn't work anymore
        assert user_service.authenticate(user.email, old_password) is None
        
        # Assert - New password works
        assert user_service.authenticate(user.email, new_password) is not None
    
    def test_get_filtered_users_with_real_data(self, user_service):
        """Test user filtering with real database."""
        # Arrange - Create multiple users
        UserFactory.create(user_service, email="alice@example.com", full_name="Alice")
        UserFactory.create(user_service, email="bob@example.com", full_name="Bob")
        UserFactory.create(user_service, email="charlie@gmail.com", full_name="Charlie")
        
        # Act - Filter by email domain
        from app.dto.user import UserFilter
        filter_params = UserFilter(email="example.com")
        result = user_service.get_filtered_users(filter_params, page=1, size=10)
        
        # Assert
        assert result.total == 2  # alice and bob
        assert len(result.items) == 2
        emails = [user.email for user in result.items]
        assert "alice@example.com" in emails
        assert "bob@example.com" in emails
        assert "charlie@gmail.com" not in emails
    
    def test_pagination_with_real_data(self, user_service):
        """Test pagination with real database."""
        # Arrange - Create 15 users
        UserFactory.create_batch(user_service, count=15)
        
        from app.dto.user import UserFilter
        filter_params = UserFilter()
        
        # Act - Get first page
        page1 = user_service.get_filtered_users(filter_params, page=1, size=5)
        
        # Assert - Page 1
        assert page1.total == 15
        assert len(page1.items) == 5
        assert page1.page == 1
        assert page1.pages == 3  # 15 / 5 = 3 pages
        
        # Act - Get second page
        page2 = user_service.get_filtered_users(filter_params, page=2, size=5)
        
        # Assert - Page 2
        assert page2.total == 15
        assert len(page2.items) == 5
        assert page2.page == 2
        
        # Assert - No duplicate users between pages
        page1_ids = [user.id for user in page1.items]
        page2_ids = [user.id for user in page2.items]
        assert set(page1_ids).isdisjoint(set(page2_ids))


@pytest.mark.integration
@pytest.mark.slow
class TestUserServicePerformance:
    """Performance tests for UserService operations."""
    
    def test_create_multiple_users_performance(self, user_service):
        """Test creating many users doesn't slow down significantly."""
        import time
        
        # Create 50 users and measure time
        start = time.time()
        users = UserFactory.create_batch(user_service, count=50)
        duration = time.time() - start
        
        # Assert
        assert len(users) == 50
        assert duration < 5.0  # Should take less than 5 seconds
        avg_time_per_user = duration / 50
        assert avg_time_per_user < 0.1  # Less than 100ms per user

