"""
FastAPI dependencies for authentication and authorization
"""

from fastapi import Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from traffic_share.server.database import get_db
from traffic_share.server.models import User, Admin, Buyer, BuyerToken
from traffic_share.core.security import SecurityManager
from traffic_share.server.config import settings


security_bearer = HTTPBearer()
security_manager = SecurityManager(secret_key=settings.SECRET_KEY)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security_bearer),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user from JWT token
    """
    try:
        token = credentials.credentials
        payload = security_manager.decode_token(token)
        
        # Verify token type
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        
        # Get user from database
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Check if user is active
        if not user.is_active or user.is_banned:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User account is inactive or banned"
            )
        
        return user
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


async def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security_bearer),
    db: Session = Depends(get_db)
) -> Admin:
    """
    Dependency to get current authenticated admin from JWT token
    """
    try:
        token = credentials.credentials
        payload = security_manager.decode_token(token)
        
        admin_id = payload.get("admin_id")
        if not admin_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required"
            )
        
        # Get admin from database
        admin = db.query(Admin).filter(Admin.id == admin_id).first()
        if not admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin not found"
            )
        
        if not admin.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin account is inactive"
            )
        
        return admin
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )


async def get_current_buyer(
    credentials: HTTPAuthorizationCredentials = Depends(security_bearer),
    db: Session = Depends(get_db)
) -> tuple[Buyer, BuyerToken]:
    """
    Dependency to get current authenticated buyer from API token
    Returns tuple of (Buyer, BuyerToken)
    """
    try:
        token = credentials.credentials
        
        # Hash the token to compare with stored hash
        token_hash = SecurityManager.hash_token(token)
        
        # Find token in database
        buyer_token = db.query(BuyerToken).filter(
            BuyerToken.token_hash == token_hash
        ).first()
        
        if not buyer_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid buyer token"
            )
        
        # Check if token is revoked
        if buyer_token.is_revoked:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked"
            )
        
        # Check if token is expired
        from datetime import datetime as dt
        if buyer_token.expires_at and buyer_token.expires_at < dt.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        
        # Get buyer
        buyer = db.query(Buyer).filter(Buyer.id == buyer_token.buyer_id).first()
        if not buyer:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Buyer not found"
            )
        
        if not buyer.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Buyer account is inactive"
            )
        
        # Update last used timestamp
        buyer_token.last_used_at = dt.utcnow()
        db.commit()
        
        return buyer, buyer_token
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed"
        )


async def get_optional_user(
    request: Request,
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Optional user dependency - returns None if not authenticated
    """
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        
        token = auth_header.split(" ")[1]
        payload = security_manager.decode_token(token)
        
        user_id = payload.get("user_id")
        if not user_id:
            return None
        
        user = db.query(User).filter(User.id == user_id).first()
        return user if user and user.is_active else None
        
    except Exception:
        return None


def verify_bot_token(request: Request):
    """
    Verify bot-to-server token for internal communication
    """
    bot_token = request.headers.get("X-Bot-Token")
    
    if not bot_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Bot token required"
        )
    
    # In production, use a secure bot token stored in env
    expected_token = settings.SECRET_KEY[:32]  # Simple example
    
    if bot_token != expected_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid bot token"
        )
    
    return True
