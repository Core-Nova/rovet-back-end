from typing import Optional
from sqlalchemy.orm import Session
import math

from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate, UserFilter, PaginatedUserResponse
from app.services.base import BaseService
from app.services.password_service import PasswordService
from app.repositories.user_repository import UserRepository
from app.exceptions.base import ConflictException, NotFoundException


class UserService(BaseService[User, UserCreate, UserUpdate]):
    def __init__(self, db: Session):
        repository = UserRepository(db)
        super().__init__(repository)
        self.password_service = PasswordService()

    def create_user(self, user_create: UserCreate) -> User:
        if self.repository.get_by_email(email=user_create.email):
            raise ConflictException(
                detail="The user with this email already exists in the system"
            )
        
        self.password_service.validate_password(user_create.password)
        
        hashed_password = self.password_service.get_password_hash(user_create.password)
        
        return self.repository.create_with_password(
            user_create=user_create,
            hashed_password=hashed_password
        )

    def authenticate(self, email: str, password: str) -> Optional[User]:
        user = self.repository.get_by_email(email=email)
        if not user:
            return None
        if not self.password_service.verify_password(password, user.hashed_password):
            return None
        return user

    def get_by_email(self, email: str) -> Optional[User]:
        return self.repository.get_by_email(email=email)

    def update_user(self, user_id: int, user_update: UserUpdate) -> User:
        current_user = self.repository.get(id=user_id)
        if not current_user:
            raise NotFoundException(detail="User not found")
        
        update_data = user_update.model_dump(exclude_unset=True)
        
        if user_update.password:
            self.password_service.validate_password(user_update.password)
            update_data["hashed_password"] = self.password_service.get_password_hash(
                user_update.password
            )
            del update_data["password"]
        
        if user_update.email and user_update.email != current_user.email:
            if self.repository.get_by_email(email=user_update.email):
                raise ConflictException(
                    detail="The user with this email already exists in the system"
                )
            current_user.email = user_update.email
        
        for field, value in update_data.items():
            if hasattr(current_user, field):
                setattr(current_user, field, value)
        
        self.repository.db.commit()
        self.repository.db.refresh(current_user)
        return current_user

    def get_filtered_users(
        self,
        filter_params: UserFilter,
        page: int = 1,
        size: int = 10
    ) -> PaginatedUserResponse:
        skip = (page - 1) * size

        users, total = self.repository.get_filtered_users(
            filter_params=filter_params,
            skip=skip,
            limit=size
        )

        pages = math.ceil(total / size)

        return PaginatedUserResponse(
            items=users,
            total=total,
            page=page,
            size=size,
            pages=pages
        ) 