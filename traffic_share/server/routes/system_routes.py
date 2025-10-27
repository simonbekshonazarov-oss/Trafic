"""
System routes - health, version, monitoring
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from traffic_share.server.database import get_db
from traffic_share.server.schemas import (
    HealthCheckResponse, VersionResponse, StandardResponse
)
from traffic_share.server.config import settings


router = APIRouter(prefix="/system", tags=["System"])


@router.get("/health", response_model=HealthCheckResponse)
async def health_check(db: Session = Depends(get_db)):
    """Health check endpoint"""
    try:
        # Test database connection
        db.execute("SELECT 1")
        
        return HealthCheckResponse(
            status="ok",
            timestamp=datetime.utcnow(),
            version=settings.APP_VERSION
        )
    except Exception as e:
        return HealthCheckResponse(
            status="error",
            timestamp=datetime.utcnow(),
            version=settings.APP_VERSION
        )


@router.get("/version", response_model=VersionResponse)
async def get_version():
    """Get API and app version info"""
    return VersionResponse(
        api_version=settings.APP_VERSION,
        app_latest=settings.APP_VERSION,
        force_update=False,
        update_url=None
    )


@router.get("/ping", response_model=StandardResponse)
async def ping():
    """Simple ping endpoint"""
    return StandardResponse(ok=True, message="pong")
