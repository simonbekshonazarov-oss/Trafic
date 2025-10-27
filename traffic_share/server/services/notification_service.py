"""
Notification service - manages system notifications
"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session

from traffic_share.server.models import Notification, User
from traffic_share.server.logger import logger


class NotificationService:
    """Notification management service"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_notification(
        self,
        user_id: Optional[int],
        type: str,
        title: str,
        message: str,
        send_via_bot: bool = False
    ) -> Notification:
        """Create a notification"""
        notification = Notification(
            user_id=user_id,
            type=type,
            title=title,
            message=message,
            sent_via_bot=send_via_bot
        )
        
        self.db.add(notification)
        self.db.commit()
        self.db.refresh(notification)
        
        logger.info(f"Notification created: {type} for user {user_id}")
        
        return notification
    
    def get_user_notifications(
        self, 
        user_id: int, 
        unread_only: bool = False
    ) -> List[Notification]:
        """Get notifications for user"""
        query = self.db.query(Notification).filter(
            Notification.user_id == user_id
        )
        
        if unread_only:
            query = query.filter(Notification.is_read == False)
        
        notifications = query.order_by(
            Notification.created_at.desc()
        ).limit(50).all()
        
        return notifications
    
    def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        """Mark notification as read"""
        notification = self.db.query(Notification).filter(
            Notification.id == notification_id,
            Notification.user_id == user_id
        ).first()
        
        if not notification:
            return False
        
        notification.is_read = True
        notification.read_at = datetime.utcnow()
        
        self.db.commit()
        
        return True
    
    def broadcast_notification(
        self,
        type: str,
        title: str,
        message: str,
        target_filter: str = "all"
    ) -> int:
        """
        Broadcast notification to multiple users
        Returns count of notifications created
        """
        # Get target users
        query = self.db.query(User).filter(User.is_active == True)
        
        if target_filter == "verified":
            query = query.filter(User.is_verified == True)
        elif target_filter.startswith("region:"):
            # Would need region field in User model
            pass
        
        users = query.all()
        
        count = 0
        for user in users:
            self.create_notification(
                user_id=user.id,
                type=type,
                title=title,
                message=message
            )
            count += 1
        
        logger.info(f"Broadcast notification sent to {count} users")
        
        return count
