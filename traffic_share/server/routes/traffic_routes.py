"""
Traffic routes - session management
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List

from traffic_share.server.database import get_db
from traffic_share.server.dependencies import get_current_user
from traffic_share.server.models import User
from traffic_share.server.schemas import (
    TrafficStartRequest, TrafficStartResponse,
    TrafficUpdateRequest, TrafficUpdateResponse,
    TrafficStopRequest, TrafficStopResponse,
    TrafficSessionResponse, TrafficSummaryResponse
)
from traffic_share.server.services.traffic_service import TrafficService
from traffic_share.core.exceptions import create_http_exception, TrafficShareException


router = APIRouter(prefix="/traffic", tags=["Traffic"])


@router.post("/start", response_model=TrafficStartResponse)
async def start_traffic_session(
    request: TrafficStartRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Start new traffic sharing session"""
    try:
        service = TrafficService(db)
        return service.start_session(current_user.id, request)
    except TrafficShareException as e:
        raise create_http_exception(e)


@router.post("/update", response_model=TrafficUpdateResponse)
async def update_traffic(
    request: TrafficUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update traffic session with new data"""
    try:
        service = TrafficService(db)
        return service.update_session(current_user.id, request)
    except TrafficShareException as e:
        raise create_http_exception(e)


@router.post("/stop", response_model=TrafficStopResponse)
async def stop_traffic_session(
    request: TrafficStopRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Stop traffic sharing session"""
    try:
        service = TrafficService(db)
        return service.stop_session(current_user.id, request)
    except TrafficShareException as e:
        raise create_http_exception(e)


@router.get("/history", response_model=List[TrafficSessionResponse])
async def get_traffic_history(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get traffic session history"""
    try:
        service = TrafficService(db)
        return service.get_session_history(current_user.id, page, page_size)
    except TrafficShareException as e:
        raise create_http_exception(e)


@router.get("/summary", response_model=TrafficSummaryResponse)
async def get_traffic_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get aggregated traffic statistics"""
    try:
        service = TrafficService(db)
        return service.get_traffic_summary(current_user.id)
    except TrafficShareException as e:
        raise create_http_exception(e)
