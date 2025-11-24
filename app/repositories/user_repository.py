from typing import Optional, Tuple, List
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserFilter
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    """
    User repository implementing data access for User entities.
    
    Provides user-specific queries and operations while maintaining
    transaction boundaries through the base repository interface.
    """

    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email address."""
        return self.get_by_condition({"email": email})

    def create_with_password(self, user_create: UserCreate, hashed_password: str) -> User:
        """
        Create user with hashed password.
        
        Note: Does NOT auto-commit. Caller must call commit() explicitly.
        This allows multiple operations in a single transaction.
        """
        db_user = User(
            email=user_create.email,
            hashed_password=hashed_password,
            full_name=user_create.full_name,
            is_active=True
        )
        self.db.add(db_user)
        return db_user

    def get_filtered_users(
        self,
        filter_params: UserFilter,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[User], int]:
        """
        Get users with filters and pagination.
        
        Returns:
            Tuple of (users list, total count)
        """
        query = self.db.query(self.model)

        if filter_params.email:
            query = query.filter(
                User.email.ilike(f"%{filter_params.email}%")
            )
        if filter_params.role is not None:
            query = query.filter(User.role == filter_params.role)
        if filter_params.is_active is not None:
            query = query.filter(User.is_active == filter_params.is_active)

        total = query.count()

        users = query.offset(skip).limit(limit).all()

        return users, total 