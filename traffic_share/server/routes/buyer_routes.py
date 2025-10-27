"""Buyer API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime

from traffic_share.server.database import get_db
from traffic_share.server.schemas import (
    PackageAllocationRequest, PackageStatusUpdateRequest, PackageResponse
)
from traffic_share.server.models import Buyer, BuyerToken, Package, PackageAllocation
from traffic_share.core.security import verify_buyer_token, hash_token
from traffic_share.core.exceptions import AuthenticationError, NotFoundError
from traffic_share.core.constants import PackageStatus

router = APIRouter()

def get_current_buyer(authorization: str, db: Session) -> Buyer:
    """Get current buyer from token."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authorization header required"
        )
    
    token = authorization.split(" ")[1]
    token_hash = hash_token(token)
    
    # Find buyer token
    buyer_token = db.query(BuyerToken).filter(
        BuyerToken.token_hash == token_hash,
        BuyerToken.is_revoked == False
    ).first()
    
    if not buyer_token:
        raise AuthenticationError("Invalid buyer token")
    
    buyer = db.query(Buyer).filter(Buyer.id == buyer_token.buyer_id).first()
    if not buyer or not buyer.is_active:
        raise AuthenticationError("Buyer not found or inactive")
    
    return buyer

@router.post("/packets/pull", response_model=dict)
async def pull_packages(
    request: PackageAllocationRequest,
    authorization: str = None,
    db: Session = Depends(get_db)
):
    """Pull available packages for buyer."""
    buyer = get_current_buyer(authorization, db)
    
    # Find available packages
    packages = db.query(Package).filter(
        Package.status == PackageStatus.AVAILABLE,
        Package.assigned_buyer_id.is_(None)
    ).limit(request.max_count).all()
    
    if not packages:
        return {"packages": []}
    
    # Allocate packages to buyer
    allocated_packages = []
    for package in packages:
        package.status = PackageStatus.ALLOCATED
        package.assigned_buyer_id = buyer.id
        package.assigned_at = datetime.utcnow()
        
        # Create allocation record
        allocation = PackageAllocation(
            package_id=package.id,
            buyer_id=buyer.id,
            status=PackageStatus.ALLOCATED
        )
        db.add(allocation)
        
        allocated_packages.append({
            "uuid": package.uuid,
            "user_id": package.user_id,
            "ip": package.ip_address,
            "size_bytes": package.size_bytes,
            "assigned_at": package.assigned_at.isoformat()
        })
    
    db.commit()
    
    return {"packages": allocated_packages}

@router.post("/packets/{uuid}/status", response_model=dict)
async def update_package_status(
    uuid: str,
    request: PackageStatusUpdateRequest,
    authorization: str = None,
    db: Session = Depends(get_db)
):
    """Update package status."""
    buyer = get_current_buyer(authorization, db)
    
    # Find package
    package = db.query(Package).filter(
        Package.uuid == uuid,
        Package.assigned_buyer_id == buyer.id
    ).first()
    
    if not package:
        raise HTTPException(
            status_code=404,
            detail="Package not found or not assigned to buyer"
        )
    
    # Update package status
    package.status = request.status
    if request.bytes_sent is not None:
        package.bytes_sent = request.bytes_sent
    
    # Update allocation record
    allocation = db.query(PackageAllocation).filter(
        PackageAllocation.package_id == package.id,
        PackageAllocation.buyer_id == buyer.id
    ).first()
    
    if allocation:
        allocation.status = request.status
        if request.status == PackageStatus.COMPLETED:
            allocation.completed_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "success": True,
        "message": "Package status updated successfully"
    }

@router.get("/me/allocations", response_model=list[PackageResponse])
async def get_my_allocations(
    authorization: str = None,
    db: Session = Depends(get_db)
):
    """Get buyer's allocated packages."""
    buyer = get_current_buyer(authorization, db)
    
    packages = db.query(Package).filter(
        Package.assigned_buyer_id == buyer.id
    ).all()
    
    return [
        PackageResponse(
            id=package.id,
            uuid=package.uuid,
            user_id=package.user_id,
            ip_address=package.ip_address,
            size_bytes=package.size_bytes,
            status=package.status,
            assigned_buyer_id=package.assigned_buyer_id,
            assigned_at=package.assigned_at,
            bytes_sent=package.bytes_sent,
            created_at=package.created_at
        )
        for package in packages
    ]
