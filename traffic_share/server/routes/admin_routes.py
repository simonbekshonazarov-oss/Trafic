"""Admin management routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from traffic_share.server.database import get_db
from traffic_share.server.schemas import (
    BuyerCreateRequest, BuyerResponse, BuyerTokenCreateRequest, BuyerTokenResponse,
    PackageCreateRequest, AdminUserResponse, AdminNotificationRequest,
    AdminReportResponse, AdminMetricsResponse
)
from traffic_share.server.models import User, Buyer, BuyerToken, Package, Admin
from traffic_share.core.security import generate_buyer_token, hash_token
from traffic_share.core.exceptions import AuthenticationError, NotFoundError

router = APIRouter()

def get_admin_user(authorization: str, db: Session) -> Admin:
    """Get admin user from token."""
    # Simplified admin authentication
    # In production, implement proper admin JWT verification
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authorization header required"
        )
    
    # For now, accept any token as admin (implement proper admin auth)
    return Admin(telegram_id=123456789, is_superadmin=True)

@router.post("/buyers", response_model=BuyerResponse)
async def create_buyer(
    request: BuyerCreateRequest,
    authorization: str = None,
    db: Session = Depends(get_db)
):
    """Create a new buyer."""
    get_admin_user(authorization, db)
    
    buyer = Buyer(
        name=request.name,
        contact=request.contact,
        region=request.region
    )
    
    db.add(buyer)
    db.commit()
    db.refresh(buyer)
    
    return BuyerResponse(
        id=buyer.id,
        name=buyer.name,
        contact=buyer.contact,
        region=buyer.region,
        is_active=buyer.is_active,
        created_at=buyer.created_at
    )

@router.get("/buyers", response_model=list[BuyerResponse])
async def get_buyers(
    authorization: str = None,
    db: Session = Depends(get_db)
):
    """Get all buyers."""
    get_admin_user(authorization, db)
    
    buyers = db.query(Buyer).all()
    
    return [
        BuyerResponse(
            id=buyer.id,
            name=buyer.name,
            contact=buyer.contact,
            region=buyer.region,
            is_active=buyer.is_active,
            created_at=buyer.created_at
        )
        for buyer in buyers
    ]

@router.post("/buyers/{buyer_id}/tokens", response_model=BuyerTokenResponse)
async def create_buyer_token(
    buyer_id: int,
    request: BuyerTokenCreateRequest,
    authorization: str = None,
    db: Session = Depends(get_db)
):
    """Create buyer token."""
    get_admin_user(authorization, db)
    
    buyer = db.query(Buyer).filter(Buyer.id == buyer_id).first()
    if not buyer:
        raise HTTPException(
            status_code=404,
            detail="Buyer not found"
        )
    
    token = generate_buyer_token()
    token_hash = hash_token(token)
    
    buyer_token = BuyerToken(
        buyer_id=buyer_id,
        token_hash=token_hash,
        description=request.description,
        expires_at=request.expires_at
    )
    
    db.add(buyer_token)
    db.commit()
    
    return BuyerTokenResponse(
        token=token,
        expires_at=request.expires_at,
        description=request.description
    )

@router.post("/packages/bulk_create", response_model=dict)
async def bulk_create_packages(
    request: PackageCreateRequest,
    authorization: str = None,
    db: Session = Depends(get_db)
):
    """Bulk create packages."""
    get_admin_user(authorization, db)
    
    created_count = 0
    errors = []
    
    for package_data in request.packages:
        try:
            package = Package(
                uuid=package_data.get("uuid"),
                user_id=package_data.get("user_id"),
                ip_address=package_data.get("ip"),
                size_bytes=package_data.get("size_bytes")
            )
            db.add(package)
            created_count += 1
        except Exception as e:
            errors.append(str(e))
    
    db.commit()
    
    return {
        "created": created_count,
        "errors": errors
    }

@router.get("/users", response_model=list[AdminUserResponse])
async def get_users(
    authorization: str = None,
    db: Session = Depends(get_db)
):
    """Get all users."""
    get_admin_user(authorization, db)
    
    users = db.query(User).all()
    
    return [
        AdminUserResponse(
            id=user.id,
            telegram_id=user.telegram_id,
            username=user.username,
            balance=user.balance,
            is_active=user.is_active,
            status=user.status,
            created_at=user.created_at,
            last_active=user.last_active
        )
        for user in users
    ]

@router.post("/notify", response_model=dict)
async def send_notification(
    request: AdminNotificationRequest,
    authorization: str = None,
    db: Session = Depends(get_db)
):
    """Send notification to users."""
    get_admin_user(authorization, db)
    
    # TODO: Implement notification sending via bot
    # This would send messages to users based on target criteria
    
    return {
        "success": True,
        "message": "Notification sent successfully"
    }

@router.get("/reports/daily", response_model=AdminReportResponse)
async def get_daily_report(
    authorization: str = None,
    db: Session = Depends(get_db)
):
    """Get daily report."""
    get_admin_user(authorization, db)
    
    # Calculate daily statistics
    today = datetime.utcnow().date()
    
    active_users = db.query(User).filter(
        User.last_active >= today
    ).count()
    
    # Simplified calculations
    total_traffic_gb = 100.0  # Calculate from traffic sessions
    total_payments = 500.0    # Calculate from payments
    new_users = 10            # Calculate from user registrations
    active_sessions = 5       # Calculate from active sessions
    
    return AdminReportResponse(
        date=today.isoformat(),
        active_users=active_users,
        total_traffic_gb=total_traffic_gb,
        total_payments=total_payments,
        new_users=new_users,
        active_sessions=active_sessions
    )

@router.get("/metrics", response_model=AdminMetricsResponse)
async def get_metrics(
    authorization: str = None,
    db: Session = Depends(get_db)
):
    """Get system metrics."""
    get_admin_user(authorization, db)
    
    # Simplified metrics
    return AdminMetricsResponse(
        requests_per_minute=60,
        error_rate=0.01,
        active_connections=10,
        memory_usage=512.5,
        cpu_usage=25.3,
        uptime_seconds=86400
    )
