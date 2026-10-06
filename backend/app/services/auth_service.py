"""
Authentication service — handles user registration, login, and token management.
"""
from sqlalchemy.orm import Session
from app.schemas.user import UserRegister, TokenResponse
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token
from app.core.exceptions import ConflictException, UnauthorizedException
import uuid


def register(db: Session, user_data: UserRegister) -> User:
    """
    Register a new citizen user.

    - Checks email uniqueness
    - Hashes password using bcrypt
    - Creates user with 'citizen' role
    """
    existing = get_user_by_email(db, user_data.email)
    if existing:
        raise ConflictException(detail="Email already registered")

    hashed = hash_password(user_data.password)
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        password_hash=hashed,
        role="citizen",
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


def authenticate(db: Session, email: str, password: str) -> TokenResponse | None:
    """
    Authenticate user by email and password.

    Returns a TokenResponse with JWT access token on success, None on failure.
    """
    user = get_user_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        return None
    access_token = create_access_token(data={"sub": str(user.id)})
    return TokenResponse(access_token=access_token, token_type="bearer")


def get_user_by_email(db: Session, email: str) -> User | None:
    """Look up a user by email address."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: uuid.UUID) -> User | None:
    """Look up a user by UUID."""
    return db.query(User).filter(User.id == user_id).first()


def get_current_user_from_token(db: Session, token: str) -> User | None:
    """
    Decode a JWT token and return the corresponding User.
    Returns None if the token is invalid or user not found.
    """
    from app.core.security import decode_access_token

    try:
        payload = decode_access_token(token)
    except ValueError:
        return None

    user_id_str = payload.get("sub")
    if not user_id_str:
        return None
    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        return None
    return get_user_by_id(db, user_id)
