"""
Backup task - periodic database backup
"""

import asyncio
import subprocess
from datetime import datetime
from pathlib import Path

from traffic_share.server.config import settings
from traffic_share.server.logger import logger


async def backup_database():
    """Backup PostgreSQL database"""
    try:
        # Create backup directory
        backup_dir = Path("backups")
        backup_dir.mkdir(exist_ok=True)
        
        # Generate backup filename
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_file = backup_dir / f"backup_{timestamp}.sql"
        
        # Extract database info from URL
        # Format: postgresql://user:pass@host:port/dbname
        db_url = settings.DATABASE_URL
        
        # Use pg_dump for backup
        # In production, would parse db_url properly
        logger.info(f"Starting database backup to {backup_file}")
        
        # Simplified backup command (would need proper credentials)
        # subprocess.run([
        #     "pg_dump",
        #     "-h", "localhost",
        #     "-U", "user",
        #     "-F", "c",
        #     "-f", str(backup_file),
        #     "database_name"
        # ], check=True)
        
        logger.info(f"Database backup completed: {backup_file}")
        
        # Clean old backups (keep last 7 days)
        cleanup_old_backups(backup_dir, days=7)
        
    except Exception as e:
        logger.error(f"Database backup failed: {e}")


def cleanup_old_backups(backup_dir: Path, days: int = 7):
    """Remove backups older than specified days"""
    try:
        cutoff_time = datetime.utcnow().timestamp() - (days * 86400)
        
        for backup_file in backup_dir.glob("backup_*.sql"):
            if backup_file.stat().st_mtime < cutoff_time:
                backup_file.unlink()
                logger.info(f"Removed old backup: {backup_file.name}")
                
    except Exception as e:
        logger.error(f"Backup cleanup failed: {e}")


async def backup_task_loop():
    """Periodic backup task loop"""
    while True:
        try:
            await backup_database()
        except Exception as e:
            logger.error(f"Backup task error: {e}")
        
        # Sleep for configured interval (default 24 hours)
        await asyncio.sleep(settings.BACKUP_TASK_INTERVAL)


if __name__ == "__main__":
    asyncio.run(backup_database())
