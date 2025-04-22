import pytest
from pydantic.v1 import EmailStr

from app.services.user_service import UserService
from app.exceptions.base import ConflictException, NotFoundException, ValidationException
from app.schemas.user import UserCreate, UserUpdate
from app.tests.utils import create_test_user


def test_create_user(db):
    user_service = UserService(db)
    user_data = UserCreate(
        email=EmailStr("test@example.com"),
        password="TestPassword123!",
        full_name="Test User"
    )
    
    user = user_service.create_user(user_data)
    assert user.email == user_data.email
    assert user.full_name == user_data.full_name
    
    with pytest.raises(ConflictException):
        user_service.create_user(user_data)
    
    weak_password_data = UserCreate(
        email=EmailStr("another@example.com"),
        password="weak",
        full_name="Another User"
    )
    with pytest.raises(ValidationException):
        user_service.create_user(weak_password_data)


def test_authenticate(db):
    user_service = UserService(db)
    password = "TestPassword123!"
    user = create_test_user(db, password=password)
    
    authenticated_user = user_service.authenticate(user.email, password)
    assert authenticated_user is not None
    assert authenticated_user.id == user.id
    
    assert user_service.authenticate(user.email, "wrong-password") is None
    
    assert user_service.authenticate("nonexistent@example.com", password) is None


def test_update_user(db):
    user_service = UserService(db)
    user = create_test_user(db)
    
    update_data = UserUpdate(
        email=EmailStr("updated@example.com"),
        full_name="Updated Name"
    )
    updated_user = user_service.update_user(user.id, update_data)
    assert updated_user.email == update_data.email
    assert updated_user.full_name == update_data.full_name
    
    with pytest.raises(NotFoundException):
        user_service.update_user(999, update_data)
    
    password_update = UserUpdate(
        email=user.email,
        password="NewPassword123!"
    )
    user_service.update_user(user.id, password_update)
    assert user_service.authenticate(user.email, "NewPassword123!") is not None
    
    weak_password_update = UserUpdate(
        email=user.email,
        password="weak"
    )
    with pytest.raises(ValidationException):
        user_service.update_user(user.id, weak_password_update) 