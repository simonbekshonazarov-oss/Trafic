"""Authentication routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import uuid

from traffic_share.server.database import get_db
from traffic_share.server.schemas import (
    RegisterRequest, LoginCodeRequest, VerifyCodeRequest, TokenResponse
)
from traffic_share.server.models import User, LoginCode
from traffic_share.core.security import generate_login_code, create_access_token, hash_token
from traffic_share.core.exceptions import AuthenticationError, NotFoundError
from traffic_share.core.constants import MESSAGES

router = APIRouter()

@router.post("/register", response_model=dict)
async def register_user(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """Register a new user."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.telegram_id == request.telegram_id).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="User already exists"
        )
    
    # Create new user
    user = User(
        telegram_id=request.telegram_id,
        username=request.username,
        phone=request.phone,
        email=request.email,
        is_verified=False
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {
        "success": True,
        "message": MESSAGES["user_created"],
        "user_id": user.id
    }

@router.post("/request_login_code", response_model=dict)
async def request_login_code(
    request: LoginCodeRequest,
    db: Session = Depends(get_db)
):
    """Request login code via Telegram."""
    # Check if user exists
    user = db.query(User).filter(User.telegram_id == request.telegram_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail=MESSAGES["user_not_found"]
        )
    
    # Generate login code
    code = generate_login_code()
    expires_at = datetime.utcnow() + timedelta(minutes=5)
    
    # Save login code
    login_code = LoginCode(
        telegram_id=request.telegram_id,
        code=code,
        expires_at=expires_at
    )
    
    db.add(login_code)
    db.commit()
    
    # Send code via Telegram bot
    from traffic_share.server.services.bot_service import bot_service
    await bot_service.send_login_code(request.telegram_id, code)
    
    return {
        "success": True,
        "message": MESSAGES["login_code_sent"]
    }

@router.post("/verify_code", response_model=TokenResponse)
async def verify_code(
    request: VerifyCodeRequest,
    db: Session = Depends(get_db)
):
    """Verify login code and return tokens."""
    # Find valid login code
    login_code = db.query(LoginCode).filter(
        LoginCode.telegram_id == request.telegram_id,
        LoginCode.code == request.code,
        LoginCode.used == False,
        LoginCode.expires_at > datetime.utcnow()
    ).first()
    
    if not login_code:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired code"
        )
    
    # Mark code as used
    login_code.used = True
    db.commit()
    
    # Get user
    user = db.query(User).filter(User.telegram_id == request.telegram_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail=MESSAGES["user_not_found"]
        )
    
    # Update user verification status
    user.is_verified = True
    user.last_active = datetime.utcnow()
    db.commit()
    
    # Create tokens
    access_token = create_access_token(
        data={"sub": str(user.id), "telegram_id": user.telegram_id}
    )
    refresh_token = create_access_token(
        data={"sub": str(user.id), "type": "refresh"},
        expires_delta=timedelta(days=7)
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=1800
    )

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    """Refresh access token."""
    # TODO: Implement refresh token logic
    # This would verify the refresh token and issue a new access token
    raise HTTPException(
        status_code=501,
        detail="Refresh token not implemented yet"
    )
