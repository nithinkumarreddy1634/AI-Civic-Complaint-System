"""
Unit tests for AuthenticationService (Section 5).
"""
import pytest
from sqlalchemy.orm import Session
from app.services import auth_service
from app.schemas.user import UserRegister
from app.core.exceptions import ConflictException


def test_auth_register_and_authenticate(db: Session):
    """Test user registration and subsequent authentication."""
    user_data = UserRegister(
        name="Unit Citizen",
        email="unit_citizen@civicai.org",
        password="securePassword123!",
    )
    user = auth_service.register(db, user_data)
    assert user.id is not None
    assert user.email == "unit_citizen@civicai.org"
    assert user.role == "citizen"

    # Authenticate with correct password
    token = auth_service.authenticate(db, "unit_citizen@civicai.org", "securePassword123!")
    assert token is not None
    assert token.access_token is not None
    assert token.token_type == "bearer"

    # Authenticate with wrong password
    bad_token = auth_service.authenticate(db, "unit_citizen@civicai.org", "wrongPassword")
    assert bad_token is None


def test_auth_duplicate_email(db: Session):
    """Test that registering duplicate email raises ConflictException."""
    user_data = UserRegister(
        name="Duplicate User",
        email="dup_user@civicai.org",
        password="password123",
    )
    auth_service.register(db, user_data)

    with pytest.raises(ConflictException):
        auth_service.register(db, user_data)


def test_get_current_user_from_token(db: Session):
    """Test decoding token back to User instance."""
    user_data = UserRegister(
        name="Token User",
        email="token_user@civicai.org",
        password="password123",
    )
    user = auth_service.register(db, user_data)
    token = auth_service.authenticate(db, user.email, "password123")

    retrieved = auth_service.get_current_user_from_token(db, token.access_token)
    assert retrieved is not None
    assert retrieved.id == user.id

    # Invalid token returns None
    assert auth_service.get_current_user_from_token(db, "invalid.jwt.token") is None
