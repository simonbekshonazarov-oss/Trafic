"""
Traffic service - manages traffic sessions and logs
"""

from datetime import datetime, timedelta
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from traffic_share.server.models import TrafficSession, TrafficLog, User
from traffic_share.server.schemas import (
    TrafficStartRequest, TrafficStartResponse,
    TrafficUpdateRequest, TrafficUpdateResponse,
    TrafficStopRequest, TrafficStopResponse,
    TrafficSessionResponse, TrafficSummaryResponse
)
from traffic_share.core.security import SecurityManager
from traffic_share.core.exceptions import (
    ResourceNotFoundError, ValidationError, SessionError
)
from traffic_share.server.utils import calculate_earnings, bytes_to_gb
from traffic_share.server.config import settings
from traffic_share.server.logger import logger


class TrafficService:
    """Traffic session management service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def start_session(
        self, 
        user_id: int, 
        request: TrafficStartRequest
    ) -> TrafficStartResponse:
        """Start new traffic session"""
        # Check if user has active session
        active_session = self.db.query(TrafficSession).filter(
            TrafficSession.user_id == user_id,
            TrafficSession.status == "active"
        ).first()
        
        if active_session:
            raise SessionError("User already has an active session")
        
        # Generate session ID
        session_id = SecurityManager.generate_uuid()
        
        # Create session
        session = TrafficSession(
            session_id=session_id,
            user_id=user_id,
            device_id=request.device_id,
            start_ip=request.public_ip,
            status="active"
        )
        
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        logger.info(f"Traffic session {session_id} started for user {user_id}")
        
        return TrafficStartResponse(
            session_id=session_id,
            ok=True
        )
    
    def update_session(
        self, 
        user_id: int, 
        request: TrafficUpdateRequest
    ) -> TrafficUpdateResponse:
        """Update traffic session with new data"""
        # Get session
        session = self.db.query(TrafficSession).filter(
            TrafficSession.session_id == request.session_id,
            TrafficSession.user_id == user_id
        ).first()
        
        if not session:
            raise ResourceNotFoundError("Session not found")
        
        if session.status != "active":
            raise SessionError("Session is not active")
        
        # Update session totals
        session.bytes_tx += request.bytes_tx
        session.bytes_rx += request.bytes_rx
        session.bytes_total = session.bytes_tx + session.bytes_rx
        session.updated_at = datetime.utcnow()
        
        # Create traffic log entry
        traffic_log = TrafficLog(
            session_id=session.id,
            bytes_tx=request.bytes_tx,
            bytes_rx=request.bytes_rx,
            interval_seconds=request.interval_seconds
        )
        
        self.db.add(traffic_log)
        self.db.commit()
        
        return TrafficUpdateResponse(ok=True)
    
    def stop_session(
        self, 
        user_id: int, 
        request: TrafficStopRequest
    ) -> TrafficStopResponse:
        """Stop traffic session"""
        # Get session
        session = self.db.query(TrafficSession).filter(
            TrafficSession.session_id == request.session_id,
            TrafficSession.user_id == user_id
        ).first()
        
        if not session:
            raise ResourceNotFoundError("Session not found")
        
        # Update final bytes
        session.bytes_tx = request.final_bytes_tx
        session.bytes_rx = request.final_bytes_rx
        session.bytes_total = session.bytes_tx + session.bytes_rx
        session.end_time = datetime.utcnow()
        session.status = "completed"
        
        # Calculate earnings
        earnings = calculate_earnings(session.bytes_total, settings.PRICE_PER_GB)
        session.earnings = earnings
        
        # Update user balance
        user = self.db.query(User).filter(User.id == user_id).first()
        if user:
            user.balance += earnings
            user.total_earned += earnings
        
        self.db.commit()
        
        logger.info(
            f"Session {request.session_id} stopped. "
            f"Total: {bytes_to_gb(session.bytes_total):.2f} GB, "
            f"Earnings: ${earnings:.2f}"
        )
        
        return TrafficStopResponse(ok=True, earnings=earnings)
    
    def get_session_history(
        self, 
        user_id: int, 
        page: int = 1, 
        page_size: int = 50
    ) -> List[TrafficSessionResponse]:
        """Get user's traffic session history"""
        offset = (page - 1) * page_size
        
        sessions = self.db.query(TrafficSession).filter(
            TrafficSession.user_id == user_id
        ).order_by(
            TrafficSession.start_time.desc()
        ).offset(offset).limit(page_size).all()
        
        return [TrafficSessionResponse.from_orm(s) for s in sessions]
    
    def get_traffic_summary(self, user_id: int) -> TrafficSummaryResponse:
        """Get aggregated traffic statistics"""
        now = datetime.utcnow()
        
        # Daily
        daily_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        daily_stats = self.db.query(
            func.sum(TrafficSession.bytes_total).label("bytes"),
            func.sum(TrafficSession.earnings).label("earnings")
        ).filter(
            TrafficSession.user_id == user_id,
            TrafficSession.start_time >= daily_start
        ).first()
        
        # Weekly
        weekly_start = now - timedelta(days=7)
        weekly_stats = self.db.query(
            func.sum(TrafficSession.bytes_total).label("bytes"),
            func.sum(TrafficSession.earnings).label("earnings")
        ).filter(
            TrafficSession.user_id == user_id,
            TrafficSession.start_time >= weekly_start
        ).first()
        
        # Monthly
        monthly_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        monthly_stats = self.db.query(
            func.sum(TrafficSession.bytes_total).label("bytes"),
            func.sum(TrafficSession.earnings).label("earnings")
        ).filter(
            TrafficSession.user_id == user_id,
            TrafficSession.start_time >= monthly_start
        ).first()
        
        # Total
        total_stats = self.db.query(
            func.sum(TrafficSession.bytes_total).label("bytes"),
            func.sum(TrafficSession.earnings).label("earnings")
        ).filter(
            TrafficSession.user_id == user_id
        ).first()
        
        return TrafficSummaryResponse(
            daily_gb=bytes_to_gb(daily_stats.bytes or 0),
            weekly_gb=bytes_to_gb(weekly_stats.bytes or 0),
            monthly_gb=bytes_to_gb(monthly_stats.bytes or 0),
            total_gb=bytes_to_gb(total_stats.bytes or 0),
            daily_earnings=daily_stats.earnings or 0.0,
            weekly_earnings=weekly_stats.earnings or 0.0,
            monthly_earnings=monthly_stats.earnings or 0.0,
            total_earnings=total_stats.earnings or 0.0
        )
