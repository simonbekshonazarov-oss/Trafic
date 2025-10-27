"""
User service - manages user profile and devices
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from traffic_share.server.models import User, Device
from traffic_share.server.schemas import (
    UserProfile, UpdateUserRequest, DeviceRegisterRequest, DeviceResponse
)
from traffic_share.core.exceptions import ResourceNotFoundError, ValidationError
from traffic_share.server.logger import logger


class UserService:
    """User management service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_user_profile(self, user_id: int) -> UserProfile:
        """Get user profile"""
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise ResourceNotFoundError("User not found")
        
        return UserProfile.from_orm(user)
    
    def update_user_profile(
        self, 
        user_id: int, 
        request: UpdateUserRequest
    ) -> UserProfile:
        """Update user profile"""
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise ResourceNotFoundError("User not found")
        
        # Update fields
        if request.phone is not None:
            user.phone = request.phone
        if request.email is not None:
            user.email = request.email
        if request.username is not None:
            user.username = request.username
        
        user.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(user)
        
        logger.info(f"User {user_id} profile updated")
        
        return UserProfile.from_orm(user)
    
    def register_device(
        self, 
        user_id: int, 
        request: DeviceRegisterRequest
    ) -> DeviceResponse:
        """Register or update user device"""
        # Check if device exists
        device = self.db.query(Device).filter(
            Device.device_id == request.device_id
        ).first()
        
        if device:
            # Update existing device
            device.user_id = user_id
            device.device_name = request.device_name or device.device_name
            device.os = request.os
            device.app_version = request.app_version
            device.last_ip = request.ip or device.last_ip
            device.last_active_at = datetime.utcnow()
            device.is_active = True
            
            logger.info(f"Device {device.device_id} updated for user {user_id}")
        else:
            # Create new device
            device = Device(
                user_id=user_id,
                device_id=request.device_id,
                device_name=request.device_name,
                os=request.os,
                app_version=request.app_version,
                last_ip=request.ip
            )
            self.db.add(device)
            logger.info(f"New device {device.device_id} registered for user {user_id}")
        
        self.db.commit()
        self.db.refresh(device)
        
        return DeviceResponse.from_orm(device)
    
    def get_user_devices(self, user_id: int) -> List[DeviceResponse]:
        """Get all devices for a user"""
        devices = self.db.query(Device).filter(
            Device.user_id == user_id
        ).order_by(Device.last_active_at.desc()).all()
        
        return [DeviceResponse.from_orm(d) for d in devices]
    
    def deactivate_device(self, user_id: int, device_id: str) -> bool:
        """Deactivate a user device"""
        device = self.db.query(Device).filter(
            Device.user_id == user_id,
            Device.device_id == device_id
        ).first()
        
        if not device:
            raise ResourceNotFoundError("Device not found")
        
        device.is_active = False
        self.db.commit()
        
        logger.info(f"Device {device_id} deactivated for user {user_id}")
        return True
    
    def get_user_balance(self, user_id: int) -> dict:
        """Get user balance details"""
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise ResourceNotFoundError("User not found")
        
        # Calculate pending earnings from active sessions
        from traffic_share.server.models import TrafficSession
        from traffic_share.server.utils import calculate_earnings
        from traffic_share.server.config import settings
        
        active_sessions = self.db.query(TrafficSession).filter(
            TrafficSession.user_id == user_id,
            TrafficSession.status == "active"
        ).all()
        
        pending_earnings = sum(
            calculate_earnings(session.bytes_total, settings.PRICE_PER_GB)
            for session in active_sessions
        )
        
        return {
            "available": user.balance,
            "pending": pending_earnings,
            "total_earned": user.total_earned,
            "currency": "USD"
        }
