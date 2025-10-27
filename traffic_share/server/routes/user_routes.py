"""User management routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from traffic_share.server.database import get_db
from traffic_share.server.schemas import (
    UserResponse, UserUpdateRequest, DeviceRegisterRequest, DeviceResponse
)
from traffic_share.server.models import User, Device
from traffic_share.core.security import verify_token
from traffic_share.core.exceptions import AuthenticationError, NotFoundError

router = APIRouter()

def get_current_user(token: str, db: Session) -> User:
    """Get current user from token."""
    try:
        payload = verify_token(token)
        user_id = payload.get("sub")
        if not user_id:
            raise AuthenticationError("Invalid token")
        
        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user:
            raise NotFoundError("User not found")
        
        return user
    except Exception as e:
        raise AuthenticationError("Invalid token")

@router.get("/me", response_model=UserResponse)
async def get_user_profile(
    authorization: str = None,
    db: Session = Depends(get_db)
):
    """Get current user profile."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authorization header required"
        )
    
    token = authorization.split(" ")[1]
    user = get_current_user(token, db)
    
    return UserResponse(
        id=user.id,
        telegram_id=user.telegram_id,
        username=user.username,
        phone=user.phone,
        email=user.email,
        balance=user.balance,
        is_verified=user.is_verified,
        is_active=user.is_active,
        status=user.status,
        created_at=user.created_at,
        last_active=user.last_active
    )

@router.post("/update", response_model=dict)
async def update_user_profile(
    request: UserUpdateRequest,
    authorization: str = None,
    db: Session = Depends(get_db)
):
    """Update user profile."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authorization header required"
        )
    
    token = authorization.split(" ")[1]
    user = get_current_user(token, db)
    
    # Update user fields
    if request.username is not None:
        user.username = request.username
    if request.phone is not None:
        user.phone = request.phone
    if request.email is not None:
        user.email = request.email
    
    user.updated_at = datetime.utcnow()
    db.commit()
    
    return {
        "success": True,
        "message": "Profile updated successfully"
    }

@router.post("/device/register", response_model=dict)
async def register_device(
    request: DeviceRegisterRequest,
    authorization: str = None,
    db: Session = Depends(get_db)
):
    """Register user device."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authorization header required"
        )
    
    token = authorization.split(" ")[1]
    user = get_current_user(token, db)
    
    # Check if device already exists
    existing_device = db.query(Device).filter(
        Device.device_id == request.device_id
    ).first()
    
    if existing_device:
        # Update existing device
        existing_device.ip_address = request.ip
        existing_device.last_active = datetime.utcnow()
        db.commit()
        return {
            "success": True,
            "message": "Device updated successfully",
            "session_id": str(existing_device.id)
        }
    
    # Create new device
    device = Device(
        user_id=user.id,
        device_id=request.device_id,
        os=request.os,
        ip_address=request.ip
    )
    
    db.add(device)
    db.commit()
    db.refresh(device)
    
    return {
        "success": True,
        "message": "Device registered successfully",
        "session_id": str(device.id)
    }

@router.get("/devices", response_model=list[DeviceResponse])
async def get_user_devices(
    authorization: str = None,
    db: Session = Depends(get_db)
):
    """Get user devices."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authorization header required"
        )
    
    token = authorization.split(" ")[1]
    user = get_current_user(token, db)
    
    devices = db.query(Device).filter(Device.user_id == user.id).all()
    
    return [
        DeviceResponse(
            id=device.id,
            device_id=device.device_id,
            os=device.os,
            ip_address=device.ip_address,
            last_active=device.last_active,
            created_at=device.created_at
        )
        for device in devices
    ]
