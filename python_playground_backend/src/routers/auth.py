from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.core.config import get_settings
from src.core.database import get_db
from src.core.models import User
from src.core.schemas import Token, UserCreate, UserLogin, UserOut
from src.core.security import (
    create_access_token,
    get_current_user,
    get_password_hash,
    verify_password,
)

router = APIRouter()
settings = get_settings()


@router.post(
    "/register",
    response_model=UserOut,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
    description="Create a new user account. Returns the created user (no token is returned).",
)
# PUBLIC_INTERFACE
def register(payload: UserCreate, db: Session = Depends(get_db)) -> UserOut:
    """
    Register a new user.

    Args:
        payload: UserCreate model containing email, password, and optional full_name.
        db: Database session.

    Returns:
        UserOut: Created user profile.

    Raises:
        HTTPException 400 if the email is already registered.
    """
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=get_password_hash(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post(
    "/login",
    response_model=Token,
    summary="Login with JSON body",
    description="Authenticate using JSON body with email and password. Returns a JWT access token.",
)
# PUBLIC_INTERFACE
def login(payload: UserLogin, db: Session = Depends(get_db)) -> Token:
    """
    Authenticate a user using JSON email/password.

    Returns:
        Token: JWT access token and token type.
    """
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(subject=str(user.id), expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    return Token(access_token=access_token, token_type="bearer")


@router.post(
    "/token",
    response_model=Token,
    summary="OAuth2 token endpoint",
    description="Authenticate using form data (username/password) as required by OAuth2PasswordBearer.",
)
# PUBLIC_INTERFACE
def login_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> Token:
    """
    OAuth2-compatible token endpoint that accepts username/password form fields.

    Returns:
        Token: JWT access token and token type.
    """
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(subject=str(user.id), expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    return Token(access_token=access_token, token_type="bearer")


@router.get(
    "/me",
    response_model=UserOut,
    summary="Get current user profile",
    description="Returns the profile of the currently authenticated user.",
)
# PUBLIC_INTERFACE
def me(current_user: User = Depends(get_current_user)) -> UserOut:
    """Return the authenticated user's profile."""
    return current_user
