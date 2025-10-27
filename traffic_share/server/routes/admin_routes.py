"""
Admin routes - management and monitoring
"""

from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from traffic_share.server.database import get_db
from traffic_share.server.dependencies import get_current_admin
from traffic_share.server.models import Admin
from traffic_share.server.schemas import (
    CreateBuyerRequest, BuyerResponse,
    CreateBuyerTokenRequest, BuyerTokenResponse,
    BuyerTokenMetadata, BuyerUsageResponse,
    BulkCreatePackagesRequest, BulkCreatePackagesResponse,
    PackageResponse, AssignPackageRequest,
    UserProfile, UserListResponse, BanUserRequest,
    NotifyRequest, DailyReportResponse,
    StandardResponse, CreateAdminRequest
)
from traffic_share.server.services.buyer_service import BuyerService
from traffic_share.server.services.admin_service import AdminService
from traffic_share.server.services.notification_service import NotificationService
from traffic_share.core.exceptions import create_http_exception, TrafficShareException


router = APIRouter(prefix="/admin", tags=["Admin"])


# ==================== Buyer Management ====================

@router.post("/buyers", response_model=BuyerResponse)
async def create_buyer(
    request: CreateBuyerRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create new buyer"""
    try:
        service = BuyerService(db)
        return service.create_buyer(request)
    except TrafficShareException as e:
        raise create_http_exception(e)


@router.get("/buyers", response_model=List[BuyerResponse])
async def get_buyers(
    is_active: Optional[bool] = None,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all buyers"""
    try:
        service = BuyerService(db)
        return service.get_buyers(is_active)
    except TrafficShareException as e:
        raise create_http_exception(e)


@router.post("/buyers/{buyer_id}/tokens", response_model=BuyerTokenResponse)
async def create_buyer_token(
    buyer_id: int = Path(...),
    request: CreateBuyerTokenRequest = ...,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Create API token for buyer"""
    try:
        request.buyer_id = buyer_id
        service = BuyerService(db)
        return service.create_buyer_token(request)
    except TrafficShareException as e:
        raise create_http_exception(e)


@router.post("/tokens/{token_id}/revoke", response_model=StandardResponse)
async def revoke_token(
    token_id: int = Path(...),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Revoke buyer token"""
    try:
        service = BuyerService(db)
        service.revoke_token(token_id)
        return StandardResponse(ok=True, message="Token revoked")
    except TrafficShareException as e:
        raise create_http_exception(e)


@router.get("/buyers/{buyer_id}/usage", response_model=BuyerUsageResponse)
async def get_buyer_usage(
    buyer_id: int = Path(...),
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get buyer usage statistics"""
    try:
        service = BuyerService(db)
        return service.get_buyer_usage(buyer_id)
    except TrafficShareException as e:
        raise create_http_exception(e)


# ==================== Package Management ====================

@router.post("/packages/bulk_create", response_model=BulkCreatePackagesResponse)
async def bulk_create_packages(
    request: BulkCreatePackagesRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Bulk create packages"""
    try:
        service = AdminService(db)
        packages_data = [pkg.dict() for pkg in request.packages]
        created, errors = service.bulk_create_packages(packages_data)
        
        return BulkCreatePackagesResponse(created=created, errors=errors)
    except TrafficShareException as e:
        raise create_http_exception(e)


@router.post("/packages/cleanup_stale_allocations", response_model=StandardResponse)
async def cleanup_stale_allocations(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Cleanup stale package allocations"""
    try:
        service = BuyerService(db)
        count = service.cleanup_stale_allocations()
        
        return StandardResponse(
            ok=True,
            message=f"Cleaned up {count} stale allocations"
        )
    except TrafficShareException as e:
        raise create_http_exception(e)


# ==================== User Management ====================

@router.get("/users")
async def get_all_users(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    is_active: Optional[bool] = None,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all users"""
    try:
        service = AdminService(db)
        users, total = service.get_all_users(page, page_size, is_active)
        
        total_pages = (total + page_size - 1) // page_size
        
        return {
            "users": [UserProfile.from_orm(u) for u in users],
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    except TrafficShareException as e:
        raise create_http_exception(e)


@router.post("/user/{user_id}/ban", response_model=StandardResponse)
async def ban_user(
    user_id: int = Path(...),
    request: BanUserRequest = ...,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Ban a user"""
    try:
        service = AdminService(db)
        service.ban_user(user_id, request.reason)
        
        return StandardResponse(ok=True, message="User banned")
    except TrafficShareException as e:
        raise create_http_exception(e)


@router.post("/notify", response_model=StandardResponse)
async def send_notification(
    request: NotifyRequest,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Send notification to users"""
    try:
        service = NotificationService(db)
        count = service.broadcast_notification(
            type="admin",
            title=request.title or "System Notification",
            message=request.message,
            target_filter=request.target
        )
        
        return StandardResponse(
            ok=True,
            message=f"Notification sent to {count} users"
        )
    except TrafficShareException as e:
        raise create_http_exception(e)


# ==================== Reports & Metrics ====================

@router.get("/reports/daily", response_model=DailyReportResponse)
async def get_daily_report(
    date: Optional[str] = None,
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get daily report"""
    try:
        service = AdminService(db)
        
        report_date = None
        if date:
            report_date = datetime.strptime(date, "%Y-%m-%d")
        
        return service.get_daily_report(report_date)
    except TrafficShareException as e:
        raise create_http_exception(e)


@router.get("/metrics")
async def get_metrics(
    current_admin: Admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get system metrics"""
    try:
        service = AdminService(db)
        return service.get_system_metrics()
    except TrafficShareException as e:
        raise create_http_exception(e)


@router.post("/create_superadmin", response_model=StandardResponse)
async def create_superadmin(
    request: CreateAdminRequest,
    db: Session = Depends(get_db)
):
    """Create superadmin (bootstrap - should be secured!)"""
    try:
        service = AdminService(db)
        admin = service.create_admin(
            telegram_id=request.telegram_id,
            username=request.username,
            role=request.role
        )
        
        return StandardResponse(
            ok=True,
            message=f"Admin {admin.id} created"
        )
    except TrafficShareException as e:
        raise create_http_exception(e)
