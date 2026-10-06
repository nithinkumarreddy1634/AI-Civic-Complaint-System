"""
Authentication API routes.

Endpoints:
    POST /api/auth/register  — Register a new citizen account
    POST /api/auth/login     — Authenticate and receive JWT token
    GET  /api/auth/me        — Get current user profile
"""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.schemas.user import UserRegister, UserResponse, TokenResponse
from app.services import auth_service
from app.api.deps import get_current_user
from app.database.session import get_db
from app.models.user import User

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new citizen user.

    - Validates email uniqueness
    - Hashes password with bcrypt
    - Assigns 'citizen' role by default
    """
    return auth_service.register(db, user_data)


@router.post("/login", response_model=TokenResponse)
async def login(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Authenticate user with email/password and return a JWT access token.
    Supports both JSON body ({"email": "...", "password": "..."}) from web clients
    and OAuth2 form data from Swagger UI.
    """
    content_type = request.headers.get("content-type", "")
    username = None
    password = None

    if "application/json" in content_type:
        try:
            body = await request.json()
            username = body.get("email") or body.get("username")
            password = body.get("password")
        except Exception:
            pass
    else:
        try:
            form = await request.form()
            username = form.get("username") or form.get("email")
            password = form.get("password")
        except Exception:
            pass

    if not username or not password:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Email and password are required.",
        )

    token = auth_service.authenticate(db, username, password)
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """
    Get the currently authenticated user's profile.
    """
    return current_user
