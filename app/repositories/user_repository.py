from typing import Optional, Tuple, List
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserFilter
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User, UserCreate, UserUpdate]):
    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        return self.get_by_condition({"email": email})

    def create_with_password(self, user_create: UserCreate, hashed_password: str) -> User:
        db_user = User(
            email=user_create.email,
            hashed_password=hashed_password,
            full_name=user_create.full_name,
            is_active=True
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def get_filtered_users(
        self,
        filter_params: UserFilter,
        skip: int = 0,
        limit: int = 100
    ) -> Tuple[List[User], int]:
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