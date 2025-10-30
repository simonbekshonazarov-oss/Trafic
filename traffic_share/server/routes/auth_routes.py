"""
Authentication routes
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from traffic_share.server.database import get_db
from traffic_share.server.schemas import (
    RegisterRequest, RegisterResponse,
    LoginCodeRequest, LoginCodeResponse,
    VerifyCodeRequest, TokenResponse,
    RefreshTokenRequest
)
from traffic_share.server.services.auth_service import AuthService
from traffic_share.core.exceptions import create_http_exception, TrafficShareException


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=RegisterResponse)
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """Register new user or update existing"""
    try:
        service = AuthService(db)
        user = service.register_user(request)
        
        return RegisterResponse(
            user_id=user.id,
            message="verification_sent" if not user.is_verified else "user_updated"
        )
    except TrafficShareException as e:
        raise create_http_exception(e)


@router.post("/request_login_code", response_model=LoginCodeResponse)
async def request_login_code(
    request: LoginCodeRequest,
    db: Session = Depends(get_db)
):
    """Request login code - will be sent via Telegram bot"""
    try:
        service = AuthService(db)
        user, code = service.generate_login_code(request.telegram_id)
        
        # Send code via Telegram bot
        from traffic_share.bot.bot import send_login_code
        
        success = await send_login_code(request.telegram_id, code)
        
        if not success:
            raise HTTPException(
                status_code=500,
                detail="Failed to send login code. Please check your Telegram ID."
            )
        
        return LoginCodeResponse(ok=True)
    except TrafficShareException as e:
        raise create_http_exception(e)


@router.post("/verify_code", response_model=TokenResponse)
async def verify_code(
    request: VerifyCodeRequest,
    db: Session = Depends(get_db)
):
    """Verify login code and get JWT tokens"""
    try:
        service = AuthService(db)
        tokens = service.verify_login_code(request.telegram_id, request.code)
        
        return tokens
    except TrafficShareException as e:
        raise create_http_exception(e)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """Refresh access token"""
    try:
        service = AuthService(db)
        tokens = service.refresh_access_token(request.refresh_token)
        
        return tokens
    except TrafficShareException as e:
        raise create_http_exception(e)
