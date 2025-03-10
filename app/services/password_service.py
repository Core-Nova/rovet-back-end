from passlib.context import CryptContext
from typing import Optional
import re

from app.exceptions.base import ValidationException

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class PasswordService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        return pwd_context.hash(password)

    @staticmethod
    def validate_password(password: str) -> Optional[str]:
        """
        Validate password strength
        Returns None if valid, error message if invalid
        """
        if len(password) < 6:
            raise ValidationException("Password must be at least 6 characters long")
        
        if not any(c.isupper() for c in password):
            raise ValidationException("Password must contain at least one uppercase letter")
        
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise ValidationException("Password must contain at least one special character")
        
        return None 