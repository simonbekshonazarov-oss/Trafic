"""
App update routes - OTA update system
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import Optional

from traffic_share.server.database import get_db
from traffic_share.server.models import AppVersion
from traffic_share.server.schemas import (
    CheckUpdateRequest, CheckUpdateResponse,
    AppVersionResponse, StandardResponse
)
from traffic_share.server.dependencies import get_current_admin
from traffic_share.server.logger import logger

router = APIRouter(prefix="/updates", tags=["App Updates"])


@router.post("/check", response_model=CheckUpdateResponse)
async def check_for_updates(
    request: CheckUpdateRequest,
    db: Session = Depends(get_db)
):
    """
    Check for app updates
    """
    try:
        # Get latest version for platform
        latest_version = db.query(AppVersion).filter(
            AppVersion.platform == request.platform,
            AppVersion.is_active == True
        ).order_by(desc(AppVersion.version_code)).first()
        
        if not latest_version:
            return CheckUpdateResponse(
                update_available=False,
                message="No updates available"
            )
        
        # Compare versions
        current_code = int(request.current_version.split('+')[-1]) if '+' in request.current_version else 0
        
        if latest_version.version_code > current_code:
            return CheckUpdateResponse(
                update_available=True,
                latest_version=latest_version.version,
                version_code=latest_version.version_code,
                download_url=latest_version.download_url,
                file_size=latest_version.file_size,
                checksum=latest_version.checksum,
                release_notes=latest_version.release_notes,
                is_mandatory=latest_version.is_mandatory,
                message="New version available!"
            )
        
        return CheckUpdateResponse(
            update_available=False,
            message="You have the latest version"
        )
        
    except Exception as e:
        logger.error(f"Check update error: {e}")
        return CheckUpdateResponse(
            update_available=False,
            message="Error checking for updates"
        )


@router.get("/latest", response_model=AppVersionResponse)
async def get_latest_version(
    platform: str = Query(..., description="Platform: android or ios"),
    db: Session = Depends(get_db)
):
    """
    Get latest app version info
    """
    try:
        version = db.query(AppVersion).filter(
            AppVersion.platform == platform,
            AppVersion.is_active == True
        ).order_by(desc(AppVersion.version_code)).first()
        
        if not version:
            return AppVersionResponse(
                ok=False,
                message="No version found for this platform"
            )
        
        return AppVersionResponse(
            ok=True,
            version=version.version,
            version_code=version.version_code,
            platform=version.platform,
            download_url=version.download_url,
            file_size=version.file_size,
            checksum=version.checksum,
            release_notes=version.release_notes,
            is_mandatory=version.is_mandatory,
            published_at=version.published_at
        )
        
    except Exception as e:
        logger.error(f"Get latest version error: {e}")
        return AppVersionResponse(
            ok=False,
            message=str(e)
        )


@router.post("/publish", response_model=StandardResponse)
async def publish_version(
    version: str,
    version_code: int,
    platform: str,
    download_url: str,
    file_size: Optional[int] = None,
    checksum: Optional[str] = None,
    release_notes: Optional[str] = None,
    is_mandatory: bool = False,
    admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Publish new app version (Admin only)
    """
    try:
        # Check if version already exists
        existing = db.query(AppVersion).filter(
            AppVersion.version == version,
            AppVersion.platform == platform
        ).first()
        
        if existing:
            return StandardResponse(
                ok=False,
                message="Version already exists"
            )
        
        # Create new version
        from datetime import datetime
        new_version = AppVersion(
            version=version,
            version_code=version_code,
            platform=platform,
            download_url=download_url,
            file_size=file_size,
            checksum=checksum,
            release_notes=release_notes,
            is_mandatory=is_mandatory,
            is_active=True,
            published_at=datetime.utcnow()
        )
        
        db.add(new_version)
        db.commit()
        
        logger.info(f"New version published: {platform} {version}")
        
        return StandardResponse(
            ok=True,
            message=f"Version {version} published successfully"
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Publish version error: {e}")
        return StandardResponse(
            ok=False,
            message=str(e)
        )


@router.post("/deactivate/{version_id}", response_model=StandardResponse)
async def deactivate_version(
    version_id: int,
    admin = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """
    Deactivate an app version (Admin only)
    """
    try:
        version = db.query(AppVersion).filter(AppVersion.id == version_id).first()
        
        if not version:
            return StandardResponse(
                ok=False,
                message="Version not found"
            )
        
        version.is_active = False
        db.commit()
        
        return StandardResponse(
            ok=True,
            message="Version deactivated"
        )
        
    except Exception as e:
        db.rollback()
        logger.error(f"Deactivate version error: {e}")
        return StandardResponse(
            ok=False,
            message=str(e)
        )
