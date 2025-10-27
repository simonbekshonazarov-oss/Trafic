"""
Clear old/stale sessions
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from traffic_share.server.database import get_db_context
from traffic_share.server.models import TrafficSession, LoginCode
from traffic_share.server.logger import logger


def clear_old_sessions(days: int = 30):
    """Clear sessions older than specified days"""
    with get_db_context() as db:
        cutoff = datetime.utcnow() - timedelta(days=days)
        
        deleted = db.query(TrafficSession).filter(
            TrafficSession.end_time < cutoff
        ).delete()
        
        logger.info(f"Deleted {deleted} old sessions")


def clear_login_codes(hours: int = 24):
    """Clear old login codes"""
    with get_db_context() as db:
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        
        deleted = db.query(LoginCode).filter(
            LoginCode.created_at < cutoff
        ).delete()
        
        logger.info(f"Deleted {deleted} old login codes")


def main():
    """Main function"""
    try:
        logger.info("Clearing old data...")
        
        clear_old_sessions(days=30)
        clear_login_codes(hours=24)
        
        logger.info("Cleanup completed!")
        
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
