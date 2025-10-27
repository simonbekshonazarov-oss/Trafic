"""
User routes - profile and device management
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from traffic_share.server.database import get_db
from traffic_share.server.dependencies import get_current_user
from traffic_share.server.models import User
from traffic_share.server.schemas import (
    UserProfile, UpdateUserRequest,
    DeviceRegisterRequest, DeviceResponse,
    BalanceResponse, StandardResponse
)
from traffic_share.server.services.user_service import UserService
from traffic_share.core.exceptions import create_http_exception, TrafficShareException


router = APIRouter(prefix="/user", tags=["User"])


@router.get("/me", response_model=UserProfile)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user profile"""
    try:
        service = UserService(db)
        return service.get_user_profile(current_user.id)
    except TrafficShareException as e:
        raise create_http_exception(e)


@router.post("/update", response_model=UserProfile)
async def update_profile(
    request: UpdateUserRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user profile"""
    try:
        service = UserService(db)
        return service.update_user_profile(current_user.id, request)
    except TrafficShareException as e:
        raise create_http_exception(e)


@router.post("/device/register", response_model=DeviceResponse)
async def register_device(
    request: DeviceRegisterRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Register or update device"""
    try:
        service = UserService(db)
        return service.register_device(current_user.id, request)
    except TrafficShareException as e:
        raise create_http_exception(e)


@router.get("/devices", response_model=List[DeviceResponse])
async def get_devices(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all user devices"""
    try:
        service = UserService(db)
        return service.get_user_devices(current_user.id)
    except TrafficShareException as e:
        raise create_http_exception(e)
