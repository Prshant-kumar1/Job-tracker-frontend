"""
Authentication routes: register, login, and refresh token.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.auth import (
    hash_password, 
    verify_password, 
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
    _is_locked_out,
    _record_failed_attempt,
    _clear_failed_attempts
)
from app.database import get_db
from app.models import User
from app.schemas import UserCreate, UserLogin, UserOut, Token, TokenRefresh
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """Create a new user account."""
    existing_user = db.query(User).filter(User.email == user_in.email).first()
    if existing_user:
        logger.warning(f"Registration attempt with existing email: {user_in.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists",
        )

    new_user = User(
        name=user_in.name,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"New user registered: {new_user.email} (ID: {new_user.id})")
    return new_user


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Authenticate a user and return JWT access and refresh tokens."""
    # Check for account lockout
    lockout_identifier = f"login:{credentials.email.lower()}"
    if _is_locked_out(lockout_identifier):
        logger.warning(f"Login attempt on locked account: {credentials.email}")
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many failed login attempts. Please try again in 15 minutes.",
            headers={"Retry-After": "900"},
        )
    
    # Generic error message on purpose so we don't reveal whether the
    # email exists (avoids account enumeration).
    invalid_credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
        headers={"WWW-Authenticate": "Bearer"},
    )

    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        _record_failed_attempt(lockout_identifier)
        logger.warning(f"Failed login attempt for email: {credentials.email}")
        raise invalid_credentials_error

    _clear_failed_attempts(lockout_identifier)
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    logger.info(f"User logged in: {user.email} (ID: {user.id})")
    return Token(access_token=access_token, refresh_token=refresh_token)


@router.post("/refresh", response_model=Token)
def refresh_token(token_refresh: TokenRefresh, db: Session = Depends(get_db)):
    """
    Exchange a valid refresh token for a new access token and refresh token.
    This allows users to stay logged in without re-entering credentials.
    """
    payload = decode_refresh_token(token_refresh.refresh_token)
    
    if payload is None:
        logger.warning("Invalid or expired refresh token attempt")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        logger.warning("Refresh token missing user ID")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    # Verify user still exists
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        logger.warning(f"Refresh token for non-existent user ID: {user_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    # Issue new tokens
    new_access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    logger.info(f"Token refreshed for user: {user.email} (ID: {user.id})")
    return Token(access_token=new_access_token, refresh_token=new_refresh_token)
