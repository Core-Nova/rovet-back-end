"""
Test data factories for generating test objects.

Factories help create consistent test data without duplication.
"""

import uuid
from datetime import datetime
from typing import Optional

from app.models.user import User, UserRole
from app.dto.user import UserCreate


class UserFactory:
    """Factory for creating test users."""
    
    @staticmethod
    def build_create_dto(**kwargs) -> UserCreate:
        """
        Build UserCreate DTO without saving to database.
        
        Use for: Unit tests where you don't need real DB
        
        Args:
            **kwargs: Override default values
            
        Returns:
            UserCreate: User creation DTO
            
        Example:
            user_data = UserFactory.build_create_dto(email="custom@example.com")
        """
        defaults = {
            "email": f"user{uuid.uuid4().hex[:8]}@example.com",
            "password": "TestPass123!",
            "full_name": "Test User"
        }
        defaults.update(kwargs)
        return UserCreate(**defaults)
    
    @staticmethod
    def create(user_service, **kwargs) -> User:
        """
        Create and save user to database.
        
        Use for: Integration tests, E2E tests
        
        Args:
            user_service: UserService instance (with real DB)
            **kwargs: Override default values
            
        Returns:
            User: Created user object
            
        Example:
            user = UserFactory.create(user_service, email="john@example.com")
        """
        user_data = UserFactory.build_create_dto(**kwargs)
        return user_service.create_user(user_data)
    
    @staticmethod
    def create_admin(user_service, db, **kwargs) -> User:
        """
        Create admin user in database.
        
        Args:
            user_service: UserService instance
            db: Database session
            **kwargs: Override default values
            
        Returns:
            User: Created admin user
            
        Example:
            admin = UserFactory.create_admin(user_service, db)
        """
        user = UserFactory.create(user_service, **kwargs)
        user.role = UserRole.ADMIN
        db.commit()
        db.refresh(user)
        return user
    
    @staticmethod
    def create_batch(user_service, count: int = 5, **kwargs) -> list[User]:
        """
        Create multiple users at once.
        
        Args:
            user_service: UserService instance
            count: Number of users to create
            **kwargs: Common attributes for all users
            
        Returns:
            list[User]: List of created users
            
        Example:
            users = UserFactory.create_batch(user_service, count=10, is_active=True)
        """
        return [
            UserFactory.create(user_service, **kwargs)
            for _ in range(count)
        ]


class TestData:
    """Common test data constants."""
    
    # Valid test data
    VALID_EMAIL = "valid@example.com"
    VALID_PASSWORD = "ValidPass123!"
    VALID_FULL_NAME = "John Doe"
    
    # Invalid test data
    INVALID_EMAIL = "not-an-email"
    WEAK_PASSWORD = "weak"
    EMPTY_NAME = ""
    
    # Edge cases
    LONG_EMAIL = f"{'a' * 64}@{'b' * 255}.com"
    LONG_PASSWORD = "A1!" + ("a" * 97)  # 100 chars total
    LONG_NAME = "A" * 100
    
    # Common weak passwords
    WEAK_PASSWORDS = [
        "password",
        "password123",
        "12345678",
        "qwerty123",
        "admin123"
    ]
    
    # Valid passwords
    VALID_PASSWORDS = [
        "SecurePass123!",
        "MyP@ssw0rd",
        "Test1234!Pass",
        "V3ryStr0ng!"
    ]


class RequestFactory:
    """Factory for creating test request payloads."""
    
    @staticmethod
    def login_request(email: str = "test@example.com", password: str = "TestPass123!"):
        """
        Build login request payload.
        
        Example:
            payload = RequestFactory.login_request()
            response = client.post("/api/v1/auth/login", json=payload)
        """
        return {
            "email": email,
            "password": password
        }
    
    @staticmethod
    def register_request(
        email: Optional[str] = None,
        password: str = "TestPass123!",
        full_name: str = "Test User"
    ):
        """
        Build registration request payload.
        
        Example:
            payload = RequestFactory.register_request(email="new@example.com")
            response = client.post("/api/v1/auth/register", json=payload)
        """
        if email is None:
            email = f"user{uuid.uuid4().hex[:8]}@example.com"
        
        return {
            "email": email,
            "password": password,
            "full_name": full_name
        }
    
    @staticmethod
    def user_update_request(**kwargs):
        """
        Build user update request payload.
        
        Example:
            payload = RequestFactory.user_update_request(email="new@example.com")
            response = client.put("/api/v1/users/1", json=payload)
        """
        return {k: v for k, v in kwargs.items() if v is not None}


class ResponseValidator:
    """Helper for validating API responses."""
    
    @staticmethod
    def assert_user_response(response_data: dict, expected_email: str = None):
        """
        Validate user response structure.
        
        Args:
            response_data: Response JSON data
            expected_email: Expected email (optional)
        """
        assert "id" in response_data
        assert "email" in response_data
        assert "full_name" in response_data
        assert "role" in response_data
        assert "is_active" in response_data
        assert "created_at" in response_data
        
        # Password should NEVER be in response
        assert "password" not in response_data
        assert "hashed_password" not in response_data
        
        if expected_email:
            assert response_data["email"] == expected_email
    
    @staticmethod
    def assert_token_response(response_data: dict):
        """
        Validate token response structure.
        
        Args:
            response_data: Response JSON data
        """
        assert "access_token" in response_data
        assert "token_type" in response_data
        assert response_data["token_type"] == "bearer"
        assert len(response_data["access_token"]) > 20  # JWT tokens are long
    
    @staticmethod
    def assert_paginated_response(response_data: dict):
        """
        Validate paginated response structure.
        
        Args:
            response_data: Response JSON data
        """
        assert "items" in response_data
        assert "total" in response_data
        assert "page" in response_data
        assert "size" in response_data
        assert "pages" in response_data
        
        assert isinstance(response_data["items"], list)
        assert isinstance(response_data["total"], int)
        assert isinstance(response_data["page"], int)
        assert isinstance(response_data["size"], int)
        assert isinstance(response_data["pages"], int)

