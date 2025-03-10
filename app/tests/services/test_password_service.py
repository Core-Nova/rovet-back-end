import pytest
from app.services.password_service import PasswordService
from app.exceptions.base import ValidationException


def test_password_hashing():
    password_service = PasswordService()
    password = "Test123"
    hashed = password_service.get_password_hash(password)
    assert password_service.verify_password(password, hashed)
    assert not password_service.verify_password("wrong", hashed)


def test_password_validation():
    password_service = PasswordService()

    # Test valid password
    valid_password = "Test123!"
    assert password_service.validate_password(valid_password) is None

    # Test password length
    with pytest.raises(ValidationException) as exc:
        password_service.validate_password("12345")
    assert "Password must be at least 6 characters long" in str(exc.value)

    # Test uppercase requirement
    with pytest.raises(ValidationException) as exc:
        password_service.validate_password("test123")
    assert "Password must contain at least one uppercase letter" in str(exc.value)
    
    # Test special character requirement
    with pytest.raises(ValidationException) as exc:
        password_service.validate_password("TestPassword123")
    assert "Password must contain at least one special character" in str(exc.value) 