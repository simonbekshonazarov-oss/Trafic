"""
Notification task - process notification queue
"""

import asyncio
from datetime import datetime

from traffic_share.server.database import get_db_context
from traffic_share.server.models import Notification
from traffic_share.server.logger import logger


def process_pending_notifications():
    """Process notifications that need to be sent"""
    with get_db_context() as db:
        try:
            # Get unsent notifications
            notifications = db.query(Notification).filter(
                Notification.sent_via_bot == False
            ).limit(100).all()
            
            if not notifications:
                return
            
            # TODO: Send via Telegram bot
            # For now, just mark as sent
            for notification in notifications:
                # In production: send to bot service
                notification.sent_via_bot = True
            
            db.commit()
            
            logger.info(f"Processed {len(notifications)} notifications")
            
        except Exception as e:
            logger.error(f"Error processing notifications: {e}")


async def notify_task_loop():
    """Periodic notification processing loop"""
    while True:
        try:
            process_pending_notifications()
        except Exception as e:
            logger.error(f"Notify task error: {e}")
        
        # Sleep for 1 minute
        await asyncio.sleep(60)


if __name__ == "__main__":
    asyncio.run(process_pending_notifications())
