import pytest
from app.services.user_service import UserService
from app.exceptions.base import ConflictException, NotFoundException, ValidationException
from app.schemas.user import UserCreate, UserUpdate
from app.tests.utils import create_test_user


def test_create_user(db):
    user_service = UserService(db)
    user_data = UserCreate(
        email="test@example.com",
        password="TestPassword123!",
        full_name="Test User"
    )
    
    # Test successful creation
    user = user_service.create_user(user_data)
    assert user.email == user_data.email
    assert user.full_name == user_data.full_name
    
    # Test duplicate email
    with pytest.raises(ConflictException):
        user_service.create_user(user_data)
    
    # Test weak password
    weak_password_data = UserCreate(
        email="another@example.com",
        password="weak",
        full_name="Another User"
    )
    with pytest.raises(ValidationException):
        user_service.create_user(weak_password_data)


def test_authenticate(db):
    user_service = UserService(db)
    password = "TestPassword123!"
    user = create_test_user(db, password=password)
    
    # Test successful authentication
    authenticated_user = user_service.authenticate(user.email, password)
    assert authenticated_user is not None
    assert authenticated_user.id == user.id
    
    # Test wrong password
    assert user_service.authenticate(user.email, "wrong-password") is None
    
    # Test non-existent user
    assert user_service.authenticate("nonexistent@example.com", password) is None


def test_update_user(db):
    user_service = UserService(db)
    user = create_test_user(db)
    
    # Test successful update
    update_data = UserUpdate(
        email="updated@example.com",
        full_name="Updated Name"
    )
    updated_user = user_service.update_user(user.id, update_data)
    assert updated_user.email == update_data.email
    assert updated_user.full_name == update_data.full_name
    
    # Test non-existent user
    with pytest.raises(NotFoundException):
        user_service.update_user(999, update_data)
    
    # Test password update
    password_update = UserUpdate(
        email=user.email,
        password="NewPassword123!"
    )
    updated_user = user_service.update_user(user.id, password_update)
    assert user_service.authenticate(user.email, "NewPassword123!") is not None
    
    # Test weak password update
    weak_password_update = UserUpdate(
        email=user.email,
        password="weak"
    )
    with pytest.raises(ValidationException):
        user_service.update_user(user.id, weak_password_update) 