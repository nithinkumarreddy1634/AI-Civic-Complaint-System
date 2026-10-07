"""
Shared API dependencies for authentication and authorization.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.services import auth_service
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Decode JWT token, fetch user from DB.
    Raises 401 if token is invalid or user not found.
    """
    user = auth_service.get_current_user_from_token(db, token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_current_user_or_default(
    token: str | None = Depends(oauth2_scheme_optional),
    db: Session = Depends(get_db),
) -> User:
    """
    Fetch user from JWT if token is provided.
    If token is missing or invalid, fall back to the default citizen account
    so citizen reporting is never blocked by expired/missing sessions.
    """
    if token:
        user = auth_service.get_current_user_from_token(db, token)
        if user:
            return user

    default_citizen = auth_service.get_user_by_email(db, "citizen@example.com")
    if default_citizen:
        return default_citizen

    fallback = db.query(User).filter(User.role == "citizen").first() or db.query(User).first()
    if fallback:
        return fallback

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials and no fallback user exists",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_current_admin(user: User = Depends(get_current_user)) -> User:
    """
    Verify the current user has admin role.
    Raises 403 if the user is not an admin.
    """
    if user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return user
