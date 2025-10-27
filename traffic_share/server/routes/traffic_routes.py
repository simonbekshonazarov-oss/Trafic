"""Traffic management routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
import uuid

from traffic_share.server.database import get_db
from traffic_share.server.schemas import (
    TrafficStartRequest, TrafficStartResponse, TrafficUpdateRequest,
    TrafficStopRequest, TrafficSessionResponse, TrafficSummaryResponse
)
from traffic_share.server.models import User, Device, TrafficSession, TrafficLog
from traffic_share.core.security import verify_token
from traffic_share.core.exceptions import AuthenticationError, NotFoundError
from traffic_share.core.constants import MESSAGES, SessionStatus

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

@router.post("/start", response_model=TrafficStartResponse)
async def start_traffic_session(
    request: TrafficStartRequest,
    authorization: str = None,
    db: Session = Depends(get_db)
):
    """Start a new traffic session."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authorization header required"
        )
    
    token = authorization.split(" ")[1]
    user = get_current_user(token, db)
    
    # Find device
    device = db.query(Device).filter(
        Device.device_id == request.device_id,
        Device.user_id == user.id
    ).first()
    
    if not device:
        raise HTTPException(
            status_code=404,
            detail="Device not found"
        )
    
    # Check if user has active session
    active_session = db.query(TrafficSession).filter(
        TrafficSession.user_id == user.id,
        TrafficSession.status == SessionStatus.ACTIVE
    ).first()
    
    if active_session:
        raise HTTPException(
            status_code=400,
            detail="User already has an active session"
        )
    
    # Create new session
    session_id = str(uuid.uuid4())
    session = TrafficSession(
        user_id=user.id,
        device_id=device.id,
        session_id=session_id,
        start_ip=request.public_ip
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return TrafficStartResponse(
        session_id=session_id,
        success=True
    )

@router.post("/update", response_model=dict)
async def update_traffic(
    request: TrafficUpdateRequest,
    authorization: str = None,
    db: Session = Depends(get_db)
):
    """Update traffic data for active session."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authorization header required"
        )
    
    token = authorization.split(" ")[1]
    user = get_current_user(token, db)
    
    # Find session
    session = db.query(TrafficSession).filter(
        TrafficSession.session_id == request.session_id,
        TrafficSession.user_id == user.id,
        TrafficSession.status == SessionStatus.ACTIVE
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=404,
            detail="Active session not found"
        )
    
    # Update session totals
    session.bytes_tx += request.bytes_tx
    session.bytes_rx += request.bytes_rx
    session.bytes_total = session.bytes_tx + session.bytes_rx
    session.updated_at = datetime.utcnow()
    
    # Create traffic log entry
    log = TrafficLog(
        session_id=session.id,
        bytes_tx=request.bytes_tx,
        bytes_rx=request.bytes_rx
    )
    
    db.add(log)
    db.commit()
    
    return {
        "success": True,
        "message": MESSAGES["traffic_updated"]
    }

@router.post("/stop", response_model=dict)
async def stop_traffic_session(
    request: TrafficStopRequest,
    authorization: str = None,
    db: Session = Depends(get_db)
):
    """Stop traffic session."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authorization header required"
        )
    
    token = authorization.split(" ")[1]
    user = get_current_user(token, db)
    
    # Find session
    session = db.query(TrafficSession).filter(
        TrafficSession.session_id == request.session_id,
        TrafficSession.user_id == user.id,
        TrafficSession.status == SessionStatus.ACTIVE
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=404,
            detail="Active session not found"
        )
    
    # Update final totals
    session.bytes_tx += request.final_bytes_tx
    session.bytes_rx += request.final_bytes_rx
    session.bytes_total = session.bytes_tx + session.bytes_rx
    session.end_time = datetime.utcnow()
    session.status = SessionStatus.COMPLETED
    session.end_ip = session.start_ip  # For now, same as start IP
    
    # Calculate earnings (simplified)
    gb_used = session.bytes_total / (1024 ** 3)
    earnings = gb_used * 0.5  # $0.50 per GB
    
    # Update user balance
    user.balance += earnings
    user.last_active = datetime.utcnow()
    
    db.commit()
    
    return {
        "success": True,
        "message": MESSAGES["session_stopped"],
        "earnings": earnings,
        "gb_used": round(gb_used, 2)
    }

@router.get("/history", response_model=list[TrafficSessionResponse])
async def get_traffic_history(
    authorization: str = None,
    db: Session = Depends(get_db)
):
    """Get traffic history for user."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authorization header required"
        )
    
    token = authorization.split(" ")[1]
    user = get_current_user(token, db)
    
    sessions = db.query(TrafficSession).filter(
        TrafficSession.user_id == user.id
    ).order_by(TrafficSession.created_at.desc()).limit(50).all()
    
    return [
        TrafficSessionResponse(
            id=session.id,
            session_id=session.session_id,
            start_time=session.start_time,
            end_time=session.end_time,
            status=session.status,
            bytes_tx=session.bytes_tx,
            bytes_rx=session.bytes_rx,
            bytes_total=session.bytes_total,
            start_ip=session.start_ip,
            end_ip=session.end_ip
        )
        for session in sessions
    ]

@router.get("/summary", response_model=TrafficSummaryResponse)
async def get_traffic_summary(
    authorization: str = None,
    db: Session = Depends(get_db)
):
    """Get traffic summary for user."""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Authorization header required"
        )
    
    token = authorization.split(" ")[1]
    user = get_current_user(token, db)
    
    # Calculate summaries (simplified)
    sessions = db.query(TrafficSession).filter(
        TrafficSession.user_id == user.id
    ).all()
    
    total_bytes = sum(session.bytes_total for session in sessions)
    total_gb = total_bytes / (1024 ** 3)
    
    return TrafficSummaryResponse(
        daily=total_gb * 0.1,  # Simplified calculation
        weekly=total_gb * 0.3,
        monthly=total_gb * 0.5,
        total=total_gb,
        sessions_count=len(sessions)
    )
