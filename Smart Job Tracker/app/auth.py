"""
Authentication utilities: password hashing and JWT creation / decoding.

Kept separate from dependencies.py so these pure functions can be unit
tested without needing a FastAPI request context.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional
from collections import defaultdict
import time
import logging

from jose import jwt, JWTError
from passlib.context import CryptContext

from app.config import settings

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Simple in-memory failed login tracker (for production, use Redis)
# Tracks: {identifier: (failed_count, lockout_until_timestamp)}
_failed_login_tracker: dict[str, tuple[int, float]] = defaultdict(lambda: (0, 0.0))
MAX_FAILED_ATTEMPTS = 5
LOCKOUT_DURATION_SECONDS = 900  # 15 minutes


def _is_locked_out(identifier: str) -> bool:
    """Check if identifier is currently locked out."""
    failed_count, lockout_until = _failed_login_tracker.get(identifier, (0, 0.0))
    if failed_count >= MAX_FAILED_ATTEMPTS:
        if time.time() < lockout_until:
            return True
        else:
            # Lockout expired, reset
            _failed_login_tracker[identifier] = (0, 0.0)
    return False


def _record_failed_attempt(identifier: str):
    """Record a failed login attempt."""
    failed_count, _ = _failed_login_tracker.get(identifier, (0, 0.0))
    failed_count += 1
    if failed_count >= MAX_FAILED_ATTEMPTS:
        lockout_until = time.time() + LOCKOUT_DURATION_SECONDS
        _failed_login_tracker[identifier] = (failed_count, lockout_until)
        logger.warning(f"Account locked out for {identifier} after {failed_count} failed attempts")
    else:
        _failed_login_tracker[identifier] = (failed_count, 0.0)


def _clear_failed_attempts(identifier: str):
    """Clear failed attempts on successful login."""
    if identifier in _failed_login_tracker:
        del _failed_login_tracker[identifier]


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a signed access token JWT containing `data` plus an expiry claim."""
    to_encode = data.copy()
    to_encode["token_type"] = "access"
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """Create a signed refresh token JWT with longer expiry."""
    to_encode = data.copy()
    to_encode["token_type"] = "refresh"
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Optional[dict]:
    """Decode a JWT, returning its payload or None if invalid/expired."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        # Verify it's an access token
        if payload.get("token_type") != "access":
            return None
        return payload
    except JWTError:
        return None


def decode_refresh_token(token: str) -> Optional[dict]:
    """Decode a refresh token, returning its payload or None if invalid/expired."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        # Verify it's a refresh token
        if payload.get("token_type") != "refresh":
            return None
        return payload
    except JWTError:
        return None
