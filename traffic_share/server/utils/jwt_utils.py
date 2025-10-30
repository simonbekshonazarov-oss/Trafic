"""
JWT token yordamchi funksiyalari
"""

from datetime import timedelta
from typing import Any, Dict, Optional

from traffic_share.core.security import SecurityManager
from traffic_share.server.config import settings


_security = SecurityManager(
    secret_key=settings.SECRET_KEY,
    algorithm=settings.JWT_ALGORITHM
)


def create_access_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """JWT access token yaratish"""
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return _security.create_access_token(data=data, expires_delta=expires_delta)


def create_refresh_token(
    data: Dict[str, Any],
    expires_delta: Optional[timedelta] = None
) -> str:
    """JWT refresh token yaratish"""
    if expires_delta is None:
        expires_delta = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return _security.create_refresh_token(data=data, expires_delta=expires_delta)


def decode_token(token: str) -> Dict[str, Any]:
    """JWT tokenni dekodlash va tekshirish"""
    return _security.decode_token(token)


__all__ = [
    "create_access_token",
    "create_refresh_token",
    "decode_token",
]
