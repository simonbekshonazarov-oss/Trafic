"""
Authentication service - handles login, registration, tokens
"""

from datetime import datetime, timedelta
from typing import Optional, Tuple
from sqlalchemy.orm import Session

from traffic_share.server.models import User, LoginCode
from traffic_share.server.schemas import RegisterRequest, TokenResponse
from traffic_share.core.security import SecurityManager
from traffic_share.core.exceptions import (
    AuthenticationError, ValidationError
)
from traffic_share.server.config import settings
from traffic_share.server.logger import logger


class AuthService:
    """Authentication service"""
    
    def __init__(self, db: Session):
        self.db = db
        self.security = SecurityManager(secret_key=settings.SECRET_KEY)
    
    def register_user(self, request: RegisterRequest) -> User:
        """Register new user or return existing one"""
        # Check if user exists
        user = self.db.query(User).filter(
            User.telegram_id == request.telegram_id
        ).first()
        
        if user:
            # Update existing user info
            if request.username:
                user.username = request.username
            if request.phone:
                user.phone = request.phone
            self.db.commit()
            self.db.refresh(user)
            logger.info(f"User {user.id} updated profile")
            return user
        
        # Create new user
        user = User(
            telegram_id=request.telegram_id,
            username=request.username,
            phone=request.phone,
            is_verified=False
        )
        
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        
        logger.info(f"New user registered: {user.id}")
        return user
    
    def generate_login_code(self, telegram_id: int) -> Tuple[User, str]:
        """
        Generate login code for user
        Returns (User, code)
        """
        # Get or create user
        user = self.db.query(User).filter(
            User.telegram_id == telegram_id
        ).first()
        
        if not user:
            raise AuthenticationError("User not found. Please register first.")
        
        # Generate 6-digit code
        code = self.security.generate_random_code(6)
        
        # Create login code record
        expires_at = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        
        login_code = LoginCode(
            user_id=user.id,
            code=code,
            expires_at=expires_at
        )
        
        self.db.add(login_code)
        self.db.commit()
        
        logger.info(f"Login code generated for user {user.id}")
        return user, code
    
    def verify_login_code(
        self, 
        telegram_id: int, 
        code: str
    ) -> TokenResponse:
        """
        Verify login code and issue tokens
        """
        # Get user
        user = self.db.query(User).filter(
            User.telegram_id == telegram_id
        ).first()
        
        if not user:
            raise AuthenticationError("Invalid credentials")
        
        # Get login code
        login_code = self.db.query(LoginCode).filter(
            LoginCode.user_id == user.id,
            LoginCode.code == code,
            LoginCode.is_used == False
        ).order_by(LoginCode.created_at.desc()).first()
        
        if not login_code:
            raise AuthenticationError("Invalid or expired code")
        
        # Check expiry
        if login_code.expires_at < datetime.utcnow():
            raise AuthenticationError("Code has expired")
        
        # Mark code as used
        login_code.is_used = True
        login_code.used_at = datetime.utcnow()
        
        # Update user
        user.is_verified = True
        user.last_login_at = datetime.utcnow()
        
        self.db.commit()
        
        # Generate tokens
        access_token = self.security.create_access_token(
            data={"user_id": user.id, "telegram_id": user.telegram_id},
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        
        refresh_token = self.security.create_refresh_token(
            data={"user_id": user.id, "telegram_id": user.telegram_id},
            expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        )
        
        logger.info(f"User {user.id} logged in successfully")
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
    
    def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """Refresh access token using refresh token"""
        try:
            # Decode refresh token
            payload = self.security.decode_token(refresh_token)
            
            # Verify token type
            if payload.get("type") != "refresh":
                raise AuthenticationError("Invalid token type")
            
            user_id = payload.get("user_id")
            
            # Verify user exists and is active
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user or not user.is_active or user.is_banned:
                raise AuthenticationError("User is not active")
            
            # Generate new tokens
            access_token = self.security.create_access_token(
                data={"user_id": user.id, "telegram_id": user.telegram_id},
                expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
            )
            
            new_refresh_token = self.security.create_refresh_token(
                data={"user_id": user.id, "telegram_id": user.telegram_id},
                expires_delta=timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
            )
            
            logger.info(f"Token refreshed for user {user.id}")
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=new_refresh_token,
                expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
            
        except Exception as e:
            logger.error(f"Token refresh failed: {e}")
            raise AuthenticationError("Invalid refresh token")
