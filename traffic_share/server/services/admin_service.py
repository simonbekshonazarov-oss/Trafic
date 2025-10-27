"""
Admin service - admin operations and monitoring
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import func, and_

from traffic_share.server.models import (
    User, Admin, TrafficSession, Payment, Package, Buyer, AuditLog
)
from traffic_share.server.schemas import DailyReportResponse, MetricsResponse
from traffic_share.core.exceptions import ResourceNotFoundError, AuthorizationError
from traffic_share.server.logger import logger
from traffic_share.server.utils import bytes_to_gb


class AdminService:
    """Admin operations service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_admin(
        self, 
        telegram_id: int, 
        username: str = None, 
        role: str = "admin",
        created_by_id: int = None
    ) -> Admin:
        """Create new admin"""
        # Check if admin exists
        existing = self.db.query(Admin).filter(
            Admin.telegram_id == telegram_id
        ).first()
        
        if existing:
            raise ValidationError("Admin already exists")
        
        admin = Admin(
            telegram_id=telegram_id,
            username=username,
            role=role,
            created_by=created_by_id
        )
        
        self.db.add(admin)
        self.db.commit()
        self.db.refresh(admin)
        
        logger.info(f"New admin created: {admin.id}")
        
        return admin
    
    def get_all_users(
        self, 
        page: int = 1, 
        page_size: int = 50,
        is_active: bool = None
    ) -> tuple[List[User], int]:
        """Get all users with pagination"""
        query = self.db.query(User)
        
        if is_active is not None:
            query = query.filter(User.is_active == is_active)
        
        total = query.count()
        
        offset = (page - 1) * page_size
        users = query.order_by(
            User.created_at.desc()
        ).offset(offset).limit(page_size).all()
        
        return users, total
    
    def ban_user(self, user_id: int, reason: str = None) -> bool:
        """Ban a user"""
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise ResourceNotFoundError("User not found")
        
        user.is_banned = True
        user.is_active = False
        
        self.db.commit()
        
        logger.info(f"User {user_id} banned. Reason: {reason}")
        
        return True
    
    def unban_user(self, user_id: int) -> bool:
        """Unban a user"""
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user:
            raise ResourceNotFoundError("User not found")
        
        user.is_banned = False
        user.is_active = True
        
        self.db.commit()
        
        logger.info(f"User {user_id} unbanned")
        
        return True
    
    def get_daily_report(self, date: datetime = None) -> DailyReportResponse:
        """Generate daily report"""
        if not date:
            date = datetime.utcnow()
        
        day_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        # Total users
        total_users = self.db.query(func.count(User.id)).scalar()
        
        # Active users (logged in today)
        active_users = self.db.query(func.count(User.id)).filter(
            User.last_login_at >= day_start
        ).scalar()
        
        # New users
        new_users = self.db.query(func.count(User.id)).filter(
            User.created_at >= day_start,
            User.created_at < day_end
        ).scalar()
        
        # Traffic stats
        traffic_stats = self.db.query(
            func.sum(TrafficSession.bytes_total).label("bytes"),
            func.sum(TrafficSession.earnings).label("earnings")
        ).filter(
            TrafficSession.start_time >= day_start,
            TrafficSession.start_time < day_end
        ).first()
        
        total_traffic_gb = bytes_to_gb(traffic_stats.bytes or 0)
        total_earnings = traffic_stats.earnings or 0.0
        
        # Payouts
        payout_stats = self.db.query(
            func.sum(Payment.amount).label("amount")
        ).filter(
            Payment.created_at >= day_start,
            Payment.created_at < day_end,
            Payment.status == "completed"
        ).first()
        
        total_payouts = payout_stats.amount or 0.0
        
        # Active sessions
        active_sessions = self.db.query(func.count(TrafficSession.id)).filter(
            TrafficSession.status == "active"
        ).scalar()
        
        return DailyReportResponse(
            date=day_start.strftime("%Y-%m-%d"),
            total_users=total_users or 0,
            active_users=active_users or 0,
            new_users=new_users or 0,
            total_traffic_gb=total_traffic_gb,
            total_earnings=total_earnings,
            total_payouts=total_payouts,
            active_sessions=active_sessions or 0
        )
    
    def get_system_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        import psutil
        import time
        
        # Database connections
        # This is simplified - in production use proper DB pool monitoring
        db_connections = 0
        
        # Active sessions
        active_sessions = self.db.query(func.count(TrafficSession.id)).filter(
            TrafficSession.status == "active"
        ).scalar()
        
        # Active buyers
        active_buyers = self.db.query(func.count(Buyer.id)).filter(
            Buyer.is_active == True
        ).scalar()
        
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        # Uptime (simplified - should track actual app start time)
        uptime_seconds = int(time.time())
        
        return {
            "requests_per_minute": 0.0,  # Would need request counter
            "active_sessions": active_sessions or 0,
            "active_buyers": active_buyers or 0,
            "db_connections": db_connections,
            "redis_connected": True,  # Would need actual Redis check
            "uptime_seconds": uptime_seconds,
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_used_mb": memory.used // (1024 * 1024)
        }
    
    def search_audit_logs(
        self,
        action: str = None,
        user_id: int = None,
        start_date: datetime = None,
        end_date: datetime = None,
        limit: int = 100
    ) -> List[AuditLog]:
        """Search audit logs"""
        query = self.db.query(AuditLog)
        
        if action:
            query = query.filter(AuditLog.action == action)
        
        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)
        
        logs = query.order_by(
            AuditLog.created_at.desc()
        ).limit(limit).all()
        
        return logs
    
    def bulk_create_packages(self, packages_data: List[Dict]) -> tuple[int, List[str]]:
        """Bulk create packages"""
        created = 0
        errors = []
        
        for pkg_data in packages_data:
            try:
                # Verify user exists
                user = self.db.query(User).filter(
                    User.id == pkg_data["user_id"]
                ).first()
                
                if not user:
                    errors.append(f"User {pkg_data['user_id']} not found")
                    continue
                
                # Create package
                package = Package(
                    uuid=pkg_data["uuid"],
                    user_id=pkg_data["user_id"],
                    ip=pkg_data["ip"],
                    size_bytes=pkg_data["size_bytes"],
                    status="available"
                )
                
                self.db.add(package)
                created += 1
                
            except Exception as e:
                errors.append(f"Error creating package: {str(e)}")
        
        if created > 0:
            self.db.commit()
        
        logger.info(f"Bulk created {created} packages, {len(errors)} errors")
        
        return created, errors
