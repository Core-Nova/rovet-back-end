"""
Database tests for UserRepository.

These tests focus on database operations:
- Test repository methods directly
- Test SQL queries and filters
- Test database constraints
- Test transactions
"""

import pytest
from sqlalchemy.exc import IntegrityError
from app.models.user import User, UserRole
from app.dto.user import UserFilter
from app.tests.factories import UserFactory


@pytest.mark.db
@pytest.mark.integration
class TestUserRepositoryBasicOperations:
    """Test basic CRUD operations."""
    
    def test_create_with_password(self, user_repository, password_service):
        """Test creating user with password in database."""
        # Arrange
        from app.dto.user import UserCreate
        user_data = UserCreate(
            email="dbtest@example.com",
            password="TestPass123!",
            full_name="DB Test User"
        )
        hashed_password = password_service.get_password_hash(user_data.password)
        
        # Act
        user = user_repository.create_with_password(user_data, hashed_password)
        
        # Assert
        assert user.id is not None
        assert user.email == "dbtest@example.com"
        assert user.hashed_password == hashed_password
        assert user.hashed_password != user_data.password  # Not plaintext
    
    def test_get_by_email(self, user_repository, user_service):
        """Test retrieving user by email."""
        # Arrange - Create user
        created_user = UserFactory.create(user_service, email="findme@example.com")
        
        # Act
        found_user = user_repository.get_by_email("findme@example.com")
        
        # Assert
        assert found_user is not None
        assert found_user.id == created_user.id
        assert found_user.email == "findme@example.com"
    
    def test_get_by_email_not_found_returns_none(self, user_repository):
        """Test that non-existent email returns None."""
        # Act
        result = user_repository.get_by_email("nonexistent@example.com")
        
        # Assert
        assert result is None
    
    def test_get_by_id(self, user_repository, user_service):
        """Test retrieving user by ID."""
        # Arrange
        user = UserFactory.create(user_service)
        
        # Act
        found_user = user_repository.get(id=user.id)
        
        # Assert
        assert found_user is not None
        assert found_user.id == user.id


@pytest.mark.db
@pytest.mark.integration
class TestUserRepositoryConstraints:
    """Test database constraints and validations."""
    
    def test_unique_email_constraint(self, user_repository, password_service):
        """Test that database enforces unique email."""
        # Arrange
        from app.dto.user import UserCreate
        user_data = UserCreate(
            email="unique@example.com",
            password="TestPass123!",
            full_name="First User"
        )
        hashed = password_service.get_password_hash(user_data.password)
        
        # Act - Create first user (should succeed)
        user1 = user_repository.create_with_password(user_data, hashed)
        assert user1.id is not None
        
        # Act & Assert - Create second user with same email (should fail)
        with pytest.raises(IntegrityError):
            user_repository.create_with_password(user_data, hashed)


@pytest.mark.db
@pytest.mark.integration
class TestUserRepositoryFiltering:
    """Test filtering and querying users."""
    
    def test_filter_by_email_partial_match(self, user_repository, user_service):
        """Test filtering users by partial email match."""
        # Arrange - Create users
        UserFactory.create(user_service, email="alice@example.com")
        UserFactory.create(user_service, email="bob@example.com")
        UserFactory.create(user_service, email="alice@gmail.com")
        
        # Act - Filter by "alice"
        filters = UserFilter(email="alice")
        users, total = user_repository.get_filtered_users(filters, skip=0, limit=10)
        
        # Assert
        assert total == 2
        assert len(users) == 2
        emails = [u.email for u in users]
        assert "alice@example.com" in emails
        assert "alice@gmail.com" in emails
        assert "bob@example.com" not in emails
    
    def test_filter_by_role(self, user_repository, user_service, db):
        """Test filtering users by role."""
        # Arrange - Create users with different roles
        user1 = UserFactory.create(user_service, email="user1@example.com")
        user2 = UserFactory.create(user_service, email="user2@example.com")
        admin = UserFactory.create(user_service, email="admin@example.com")
        
        # Make one admin
        admin.role = UserRole.ADMIN
        db.commit()
        
        # Act - Filter by USER role
        filters = UserFilter(role=UserRole.USER)
        users, total = user_repository.get_filtered_users(filters, skip=0, limit=10)
        
        # Assert
        assert total == 2
        emails = [u.email for u in users]
        assert "user1@example.com" in emails
        assert "user2@example.com" in emails
        assert "admin@example.com" not in emails
    
    def test_filter_by_is_active(self, user_repository, user_service, db):
        """Test filtering users by active status."""
        # Arrange - Create active and inactive users
        active_user = UserFactory.create(user_service, email="active@example.com")
        inactive_user = UserFactory.create(user_service, email="inactive@example.com")
        
        # Make one inactive
        inactive_user.is_active = False
        db.commit()
        
        # Act - Filter by active=True
        filters = UserFilter(is_active=True)
        users, total = user_repository.get_filtered_users(filters, skip=0, limit=10)
        
        # Assert
        emails = [u.email for u in users]
        assert "active@example.com" in emails
        assert "inactive@example.com" not in emails
    
    def test_combined_filters(self, user_repository, user_service):
        """Test combining multiple filters."""
        # Arrange - Create users
        UserFactory.create(user_service, email="alice@example.com")  # Active by default
        UserFactory.create(user_service, email="bob@example.com")
        UserFactory.create(user_service, email="alice@gmail.com")
        
        # Act - Filter by email AND active status
        filters = UserFilter(email="alice", is_active=True)
        users, total = user_repository.get_filtered_users(filters, skip=0, limit=10)
        
        # Assert
        assert total == 2
        assert all("alice" in u.email for u in users)
        assert all(u.is_active for u in users)


@pytest.mark.db
@pytest.mark.integration
class TestUserRepositoryPagination:
    """Test pagination functionality."""
    
    def test_pagination_skip_and_limit(self, user_repository, user_service):
        """Test pagination with skip and limit."""
        # Arrange - Create 10 users
        created_users = UserFactory.create_batch(user_service, count=10)
        
        # Act - Get first page (5 items)
        filters = UserFilter()
        page1, total = user_repository.get_filtered_users(filters, skip=0, limit=5)
        
        # Assert - First page
        assert total == 10
        assert len(page1) == 5
        
        # Act - Get second page (skip 5, limit 5)
        page2, total = user_repository.get_filtered_users(filters, skip=5, limit=5)
        
        # Assert - Second page
        assert total == 10
        assert len(page2) == 5
        
        # Assert - No duplicates between pages
        page1_ids = [u.id for u in page1]
        page2_ids = [u.id for u in page2]
        assert set(page1_ids).isdisjoint(set(page2_ids))
    
    def test_pagination_last_partial_page(self, user_repository, user_service):
        """Test pagination when last page is not full."""
        # Arrange - Create 12 users
        UserFactory.create_batch(user_service, count=12)
        
        # Act - Get last page (skip 10, limit 5)
        filters = UserFilter()
        last_page, total = user_repository.get_filtered_users(filters, skip=10, limit=5)
        
        # Assert - Last page has only 2 items
        assert total == 12
        assert len(last_page) == 2
    
    def test_pagination_empty_page(self, user_repository, user_service):
        """Test pagination beyond available data."""
        # Arrange - Create 5 users
        UserFactory.create_batch(user_service, count=5)
        
        # Act - Try to get page beyond data
        filters = UserFilter()
        empty_page, total = user_repository.get_filtered_users(filters, skip=100, limit=10)
        
        # Assert
        assert total == 5
        assert len(empty_page) == 0


@pytest.mark.db
@pytest.mark.integration
class TestUserRepositoryTransactions:
    """Test transaction handling."""
    
    def test_transaction_rollback_on_error(self, user_repository, password_service, db):
        """Test that transaction rolls back on error."""
        # Arrange
        from app.dto.user import UserCreate
        user_data = UserCreate(
            email="rollback@example.com",
            password="TestPass123!",
            full_name="Rollback Test"
        )
        hashed = password_service.get_password_hash(user_data.password)
        
        # Act - Create user but don't commit
        user = user_repository.create_with_password(user_data, hashed)
        user_id = user.id
        
        # Rollback
        db.rollback()
        
        # Assert - User should not exist after rollback
        found_user = user_repository.get(id=user_id)
        assert found_user is None
    
    def test_transaction_commit_persists_data(self, user_repository, password_service, db):
        """Test that commit persists data."""
        # Arrange
        from app.dto.user import UserCreate
        user_data = UserCreate(
            email="commit@example.com",
            password="TestPass123!",
            full_name="Commit Test"
        )
        hashed = password_service.get_password_hash(user_data.password)
        
        # Act - Create and commit
        user = user_repository.create_with_password(user_data, hashed)
        db.commit()
        
        # Clear session to force fresh query
        db.expire_all()
        
        # Assert - User persists after commit
        found_user = user_repository.get_by_email("commit@example.com")
        assert found_user is not None
        assert found_user.id == user.id

