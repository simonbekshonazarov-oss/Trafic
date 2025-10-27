"""
Buyer service - manages buyers, tokens, and package allocation
"""

from datetime import datetime, timedelta
from typing import List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from traffic_share.server.models import (
    Buyer, BuyerToken, Package, PackageAllocation
)
from traffic_share.server.schemas import (
    CreateBuyerRequest, BuyerResponse,
    CreateBuyerTokenRequest, BuyerTokenResponse,
    PullPacketsRequest, PacketInfo, PullPacketsResponse,
    UpdatePacketStatusRequest, BuyerUsageResponse
)
from traffic_share.core.security import SecurityManager
from traffic_share.core.exceptions import (
    ResourceNotFoundError, PackageAllocationError, ValidationError
)
from traffic_share.server.config import settings
from traffic_share.server.logger import logger
from traffic_share.server.utils import create_audit_log


class BuyerService:
    """Buyer and package allocation service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_buyer(self, request: CreateBuyerRequest) -> BuyerResponse:
        """Create new buyer"""
        buyer = Buyer(
            name=request.name,
            contact=request.contact,
            region=request.region
        )
        
        self.db.add(buyer)
        self.db.commit()
        self.db.refresh(buyer)
        
        logger.info(f"New buyer created: {buyer.id} - {buyer.name}")
        
        return BuyerResponse.from_orm(buyer)
    
    def get_buyers(self, is_active: bool = None) -> List[BuyerResponse]:
        """Get all buyers"""
        query = self.db.query(Buyer)
        
        if is_active is not None:
            query = query.filter(Buyer.is_active == is_active)
        
        buyers = query.order_by(Buyer.created_at.desc()).all()
        
        return [BuyerResponse.from_orm(b) for b in buyers]
    
    def create_buyer_token(
        self, 
        request: CreateBuyerTokenRequest
    ) -> BuyerTokenResponse:
        """Create new API token for buyer"""
        # Verify buyer exists
        buyer = self.db.query(Buyer).filter(
            Buyer.id == request.buyer_id
        ).first()
        
        if not buyer:
            raise ResourceNotFoundError("Buyer not found")
        
        # Generate token
        plain_token = SecurityManager.generate_api_token(32)
        token_hash = SecurityManager.hash_token(plain_token)
        
        # Create token record
        buyer_token = BuyerToken(
            buyer_id=request.buyer_id,
            token_hash=token_hash,
            description=request.description,
            expires_at=request.expires_at
        )
        
        self.db.add(buyer_token)
        self.db.commit()
        self.db.refresh(buyer_token)
        
        logger.info(f"New token created for buyer {buyer.id}")
        
        create_audit_log(
            self.db,
            action="create_buyer_token",
            entity_type="buyer_token",
            entity_id=buyer_token.id,
            buyer_id=buyer.id,
            details={"description": request.description}
        )
        
        return BuyerTokenResponse(
            token=plain_token,  # Return plain token only once!
            token_id=buyer_token.id,
            description=buyer_token.description,
            expires_at=buyer_token.expires_at
        )
    
    def revoke_token(self, token_id: int) -> bool:
        """Revoke a buyer token"""
        token = self.db.query(BuyerToken).filter(
            BuyerToken.id == token_id
        ).first()
        
        if not token:
            raise ResourceNotFoundError("Token not found")
        
        token.is_revoked = True
        self.db.commit()
        
        logger.info(f"Token {token_id} revoked for buyer {token.buyer_id}")
        
        return True
    
    def pull_packets(
        self, 
        buyer_id: int, 
        request: PullPacketsRequest
    ) -> PullPacketsResponse:
        """
        Allocate packages to buyer (atomic operation)
        Enforces: one user + one IP = one package rule
        """
        # Get available packages
        query = self.db.query(Package).filter(
            Package.status == "available",
            Package.assigned_buyer_id.is_(None)
        )
        
        if request.region:
            # Filter by region if needed (would need region column in Package)
            pass
        
        # Use FOR UPDATE SKIP LOCKED for atomic allocation
        packages = query.limit(request.max_count).with_for_update(
            skip_locked=True
        ).all()
        
        if not packages:
            # No packages available
            return PullPacketsResponse(packages=[])
        
        allocated_packages = []
        
        for package in packages:
            # Check if buyer already has package for this user+ip combination
            existing = self.db.query(Package).filter(
                and_(
                    Package.user_id == package.user_id,
                    Package.ip == package.ip,
                    Package.assigned_buyer_id == buyer_id,
                    or_(
                        Package.status == "allocated",
                        Package.status == "in_progress"
                    )
                )
            ).first()
            
            if existing:
                # Skip this package - buyer already has one for this user+ip
                logger.warning(
                    f"Buyer {buyer_id} already has package for "
                    f"user {package.user_id} ip {package.ip}"
                )
                continue
            
            # Allocate package
            package.assigned_buyer_id = buyer_id
            package.status = "allocated"
            package.allocated_at = datetime.utcnow()
            
            # Create allocation record
            allocation = PackageAllocation(
                package_id=package.id,
                buyer_id=buyer_id,
                status="allocated",
                allocated_at=datetime.utcnow()
            )
            self.db.add(allocation)
            
            allocated_packages.append(PacketInfo(
                uuid=package.uuid,
                user_id=package.user_id,
                ip=package.ip,
                size_bytes=package.size_bytes,
                assigned_at=package.allocated_at
            ))
        
        self.db.commit()
        
        logger.info(
            f"Buyer {buyer_id} pulled {len(allocated_packages)} packages"
        )
        
        return PullPacketsResponse(packages=allocated_packages)
    
    def update_packet_status(
        self, 
        buyer_id: int, 
        uuid: str, 
        request: UpdatePacketStatusRequest
    ) -> bool:
        """Update packet status"""
        # Get package
        package = self.db.query(Package).filter(
            Package.uuid == uuid,
            Package.assigned_buyer_id == buyer_id
        ).first()
        
        if not package:
            raise ResourceNotFoundError("Package not found or not assigned to you")
        
        # Validate status transition
        valid_statuses = ["in_progress", "completed", "failed"]
        if request.status not in valid_statuses:
            raise ValidationError(f"Invalid status: {request.status}")
        
        # Update package
        package.status = request.status
        
        if request.bytes_sent is not None:
            package.bytes_sent = request.bytes_sent
        
        if request.status == "completed":
            package.completed_at = datetime.utcnow()
        
        # Update allocation record
        allocation = self.db.query(PackageAllocation).filter(
            PackageAllocation.package_id == package.id,
            PackageAllocation.buyer_id == buyer_id,
            PackageAllocation.completed_at.is_(None)
        ).order_by(PackageAllocation.allocated_at.desc()).first()
        
        if allocation:
            allocation.status = request.status
            if request.bytes_sent is not None:
                allocation.bytes_sent = request.bytes_sent
            if request.status in ["completed", "failed"]:
                allocation.completed_at = datetime.utcnow()
        
        self.db.commit()
        
        logger.info(f"Package {uuid} status updated to {request.status}")
        
        return True
    
    def get_buyer_allocations(self, buyer_id: int) -> List[dict]:
        """Get active allocations for buyer"""
        packages = self.db.query(Package).filter(
            Package.assigned_buyer_id == buyer_id,
            or_(
                Package.status == "allocated",
                Package.status == "in_progress"
            )
        ).all()
        
        return [
            {
                "uuid": p.uuid,
                "user_id": p.user_id,
                "ip": p.ip,
                "size_bytes": p.size_bytes,
                "status": p.status,
                "allocated_at": p.allocated_at,
                "bytes_sent": p.bytes_sent
            }
            for p in packages
        ]
    
    def get_buyer_usage(self, buyer_id: int) -> BuyerUsageResponse:
        """Get buyer usage statistics"""
        from sqlalchemy import func
        
        # Count by status
        stats = self.db.query(
            Package.status,
            func.count(Package.id).label("count"),
            func.sum(Package.bytes_sent).label("bytes")
        ).filter(
            Package.assigned_buyer_id == buyer_id
        ).group_by(Package.status).all()
        
        total_assigned = 0
        active = 0
        completed = 0
        failed = 0
        total_bytes = 0
        
        for stat in stats:
            if stat.status == "allocated":
                active += stat.count
            elif stat.status == "in_progress":
                active += stat.count
            elif stat.status == "completed":
                completed += stat.count
            elif stat.status == "failed":
                failed += stat.count
            
            total_assigned += stat.count
            total_bytes += stat.bytes or 0
        
        return BuyerUsageResponse(
            buyer_id=buyer_id,
            total_assigned=total_assigned,
            active=active,
            completed=completed,
            failed=failed,
            total_bytes_sent=total_bytes
        )
    
    def cleanup_stale_allocations(self) -> int:
        """
        Cleanup packages that were allocated but not confirmed
        Returns number of cleaned packages
        """
        ttl_threshold = datetime.utcnow() - timedelta(
            seconds=settings.PACKAGE_ALLOCATION_TTL
        )
        
        stale_packages = self.db.query(Package).filter(
            Package.status == "allocated",
            Package.allocated_at < ttl_threshold
        ).all()
        
        count = 0
        for package in stale_packages:
            package.status = "available"
            package.assigned_buyer_id = None
            package.allocated_at = None
            count += 1
        
        if count > 0:
            self.db.commit()
            logger.info(f"Cleaned up {count} stale package allocations")
        
        return count
