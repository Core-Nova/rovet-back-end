"""
User service module containing business logic for user operations.

This service follows the Dependency Inversion Principle:
- Depends on abstractions (UserRepository, PasswordService)
- Dependencies are injected via constructor
- Easy to test with mocks
"""

from typing import Optional
import math

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserFilter, PaginatedUserResponse
from app.services.base import BaseService
from app.services.password_service import PasswordService
from app.repositories.user_repository import UserRepository
from app.exceptions.base import ConflictException, NotFoundException


class UserService(BaseService[User, UserCreate, UserUpdate]):
    """
    User service for handling user business logic.
    
    Responsibilities:
    - User creation with password hashing
    - User authentication
    - User updates
    - Email uniqueness validation
    - User filtering and pagination
    
    Dependencies are injected, not created:
    - UserRepository: for data access
    - PasswordService: for password operations
    """
    
    def __init__(
        self,
        repository: UserRepository,
        password_service: PasswordService
    ):
        """
        Initialize UserService with injected dependencies.
        
        Args:
            repository: UserRepository for database operations
            password_service: PasswordService for password hashing/validation
            
        Example:
            ```python
            # In production (via DI):
            repo = UserRepository(db)
            pwd_service = PasswordService()
            service = UserService(repo, pwd_service)
            
            # In tests (with mocks):
            mock_repo = MagicMock(spec=UserRepository)
            mock_pwd = MagicMock(spec=PasswordService)
            service = UserService(mock_repo, mock_pwd)
            ```
        """
        super().__init__(repository)
        self.password_service = password_service

    def create_user(self, user_create: UserCreate) -> User:
        """
        Create a new user with password hashing and validation.
        
        Business rules:
        - Email must be unique
        - Password must meet complexity requirements
        - Password is hashed before storage
        
        Args:
            user_create: User creation data
            
        Returns:
            User: Created user object
            
        Raises:
            ConflictException: If email already exists
            ValidationException: If password doesn't meet requirements
            
        Example:
            ```python
            user_data = UserCreate(
                email="user@example.com",
                password="SecurePass123!",
                full_name="John Doe"
            )
            user = service.create_user(user_data)
            ```
        """
        try:
            # Check if email already exists
            if self.repository.get_by_email(email=user_create.email):
                raise ConflictException(
                    detail="The user with this email already exists in the system"
                )
            
            # Validate password complexity
            self.password_service.validate_password(user_create.password)
            
            # Hash password
            hashed_password = self.password_service.get_password_hash(user_create.password)
            
            # Create user via repository (does not commit)
            user = self.repository.create_with_password(
                user_create=user_create,
                hashed_password=hashed_password
            )
            
            # Commit transaction
            self.repository.commit()
            self.repository.refresh(user)
            
            return user
        except Exception:
            self.repository.rollback()
            raise

    def authenticate(self, email: str, password: str) -> Optional[User]:
        """
        Authenticate user with email and password.
        
        Args:
            email: User email address
            password: Plain text password
            
        Returns:
            User: Authenticated user object, or None if invalid
            
        Example:
            ```python
            user = service.authenticate("user@example.com", "password123")
            if user:
                # Authentication successful
                pass
            else:
                # Invalid credentials
                pass
            ```
        """
        # Get user by email
        user = self.repository.get_by_email(email=email)
        if not user:
            return None
            
        # Verify password
        if not self.password_service.verify_password(password, user.hashed_password):
            return None
            
        return user

    def get_by_email(self, email: str) -> Optional[User]:
        """
        Get user by email address.
        
        Args:
            email: User email address
            
        Returns:
            User: User object or None if not found
            
        Example:
            ```python
            user = service.get_by_email("user@example.com")
            ```
        """
        return self.repository.get_by_email(email=email)

    def update_user(self, user_id: int, user_update: UserUpdate) -> User:
        """
        Update user information.
        
        Business rules:
        - User must exist
        - If email changes, new email must be unique
        - If password changes, it must meet complexity requirements
        
        Args:
            user_id: User ID to update
            user_update: Update data
            
        Returns:
            User: Updated user object
            
        Raises:
            NotFoundException: If user doesn't exist
            ConflictException: If new email already exists
            ValidationException: If new password invalid
            
        Example:
            ```python
            update_data = UserUpdate(
                email="newemail@example.com",
                full_name="Jane Doe"
            )
            updated_user = service.update_user(1, update_data)
            ```
        """
        try:
            # Get current user
            current_user = self.repository.get(id=user_id)
            if not current_user:
                raise NotFoundException(detail="User not found")
            
            # Get update data (only fields that were set)
            update_data = user_update.model_dump(exclude_unset=True)
            
            # Handle password update
            if user_update.password:
                self.password_service.validate_password(user_update.password)
                update_data["hashed_password"] = self.password_service.get_password_hash(
                    user_update.password
                )
                del update_data["password"]
            
            # Handle email update
            if user_update.email and user_update.email != current_user.email:
                if self.repository.get_by_email(email=user_update.email):
                    raise ConflictException(
                        detail="The user with this email already exists in the system"
                    )
            
            # Apply updates through repository (does not commit)
            updated_user = self.repository.update(current_user, update_data)
            
            # Commit transaction
            self.repository.commit()
            self.repository.refresh(updated_user)
            
            return updated_user
        except Exception:
            self.repository.rollback()
            raise

    def get_filtered_users(
        self,
        filter_params: UserFilter,
        page: int = 1,
        size: int = 10
    ) -> PaginatedUserResponse:
        """
        Get users with filtering and pagination.
        
        Args:
            filter_params: Filter criteria (email, role, is_active)
            page: Page number (1-indexed)
            size: Page size (items per page)
            
        Returns:
            PaginatedUserResponse: Paginated list of users with metadata
            
        Example:
            ```python
            filters = UserFilter(email="john", is_active=True)
            result = service.get_filtered_users(filters, page=1, size=20)
            
            print(f"Total users: {result.total}")
            print(f"Page {result.page} of {result.pages}")
            for user in result.items:
                print(user.email)
            ```
        """
        skip = (page - 1) * size

        # Get users from repository
        users, total = self.repository.get_filtered_users(
            filter_params=filter_params,
            skip=skip,
            limit=size
        )

        # Calculate pagination metadata
        pages = math.ceil(total / size) if total > 0 else 1

        return PaginatedUserResponse(
            items=users,
            total=total,
            page=page,
            size=size,
            pages=pages
        )
