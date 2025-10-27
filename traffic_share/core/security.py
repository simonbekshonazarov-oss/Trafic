"""Security utilities for authentication and authorization."""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Optional, Union
from jose import JWTError, jwt
from passlib.context import CryptContext
from .exceptions import AuthenticationError, AuthorizationError

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, "secret-key", algorithm="HS256")
    return encoded_jwt

def verify_token(token: str) -> dict:
    """Verify and decode JWT token."""
    try:
        payload = jwt.decode(token, "secret-key", algorithms=["HS256"])
        return payload
    except JWTError:
        raise AuthenticationError("Invalid token")

def generate_login_code() -> str:
    """Generate 6-digit login code."""
    return str(secrets.randbelow(900000) + 100000)

def hash_token(token: str) -> str:
    """Hash token for secure storage."""
    return hashlib.sha256(token.encode()).hexdigest()

def generate_buyer_token() -> str:
    """Generate secure buyer API token."""
    return secrets.token_urlsafe(32)

def verify_buyer_token(provided_token: str, stored_hash: str) -> bool:
    """Verify buyer token against stored hash."""
    return hash_token(provided_token) == stored_hash

def is_admin(telegram_id: int, admin_ids: list) -> bool:
    """Check if user is admin."""
    return telegram_id in admin_ids

def check_rate_limit(identifier: str, limit: int, window: int = 60) -> bool:
    """Check if request is within rate limit."""
    # This would integrate with Redis for actual rate limiting
    # For now, return True (no rate limiting)
    return True
