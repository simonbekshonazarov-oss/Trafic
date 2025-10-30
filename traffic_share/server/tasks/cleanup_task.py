"""
Cleanup task - removes stale data and expired sessions
"""

import asyncio
from datetime import datetime, timedelta

from traffic_share.server.database import get_db_context
from traffic_share.server.models import LoginCode, TrafficSession, Package
from traffic_share.server.config import settings
from traffic_share.server.logger import logger


def cleanup_expired_login_codes():
    """Delete expired login codes"""
    with get_db_context() as db:
        try:
            # Delete login codes older than 1 day
            cutoff = datetime.utcnow() - timedelta(days=1)
            
            deleted = db.query(LoginCode).filter(
                LoginCode.expires_at < cutoff
            ).delete()
            
            if deleted > 0:
                logger.info(f"Deleted {deleted} expired login codes")
                
        except Exception as e:
            logger.error(f"Error cleaning login codes: {e}")


def cleanup_stale_sessions():
    """Mark stale active sessions as failed"""
    with get_db_context() as db:
        try:
            # Sessions active for more than 24 hours without update
            cutoff = datetime.utcnow() - timedelta(hours=24)
            
            stale_sessions = db.query(TrafficSession).filter(
                TrafficSession.status == "active",
                TrafficSession.updated_at < cutoff
            ).all()
            
            for session in stale_sessions:
                session.status = "failed"
                session.end_time = datetime.utcnow()
            
            if stale_sessions:
                db.commit()
                logger.info(f"Marked {len(stale_sessions)} stale sessions as failed")
                
        except Exception as e:
            logger.error(f"Error cleaning stale sessions: {e}")


def cleanup_stale_packages():
    """Reset stale allocated packages to available"""
    with get_db_context() as db:
        try:
            from traffic_share.server.services.buyer_service import BuyerService
            
            service = BuyerService(db)
            count = service.cleanup_stale_allocations()
            
            if count > 0:
                logger.info(f"Cleaned {count} stale package allocations")
                
        except Exception as e:
            logger.error(f"Error cleaning stale packages: {e}")


async def run_cleanup_tasks():
    """Run all cleanup tasks"""
    logger.info("Running cleanup tasks...")
    
    cleanup_expired_login_codes()
    cleanup_stale_sessions()
    cleanup_stale_packages()
    
    logger.info("Cleanup tasks completed")


async def cleanup_task_loop():
    """Periodic cleanup task loop"""
    while True:
        try:
            await run_cleanup_tasks()
        except Exception as e:
            logger.error(f"Cleanup task error: {e}")
        
        # Sleep for configured interval (default 5 minutes)
        await asyncio.sleep(settings.CLEANUP_TASK_INTERVAL)


if __name__ == "__main__":
    asyncio.run(run_cleanup_tasks())
