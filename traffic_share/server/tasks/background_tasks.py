"""Background tasks for the application."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List
from sqlalchemy.orm import Session
from traffic_share.server.database import SessionLocal
from traffic_share.server.models import User, TrafficSession, Payment, LoginCode
from traffic_share.core.constants import SessionStatus, PaymentStatus
from traffic_share.server.services.traffic_monitor import traffic_monitor

logger = logging.getLogger(__name__)

class BackgroundTaskManager:
    """Manages background tasks."""
    
    def __init__(self):
        self.tasks = []
        self.running = False
    
    async def start(self):
        """Start all background tasks."""
        if self.running:
            return
        
        self.running = True
        logger.info("Starting background tasks")
        
        # Start traffic monitoring
        self.tasks.append(asyncio.create_task(traffic_monitor.start_monitoring()))
        
        # Start cleanup tasks
        self.tasks.append(asyncio.create_task(self.cleanup_expired_codes()))
        self.tasks.append(asyncio.create_task(self.cleanup_stale_sessions()))
        self.tasks.append(asyncio.create_task(self.process_payments()))
        self.tasks.append(asyncio.create_task(self.update_statistics()))
        
        logger.info(f"Started {len(self.tasks)} background tasks")
    
    async def stop(self):
        """Stop all background tasks."""
        if not self.running:
            return
        
        self.running = False
        logger.info("Stopping background tasks")
        
        # Stop traffic monitoring
        await traffic_monitor.stop_monitoring()
        
        # Cancel all tasks
        for task in self.tasks:
            task.cancel()
        
        # Wait for tasks to complete
        await asyncio.gather(*self.tasks, return_exceptions=True)
        
        self.tasks.clear()
        logger.info("All background tasks stopped")
    
    async def cleanup_expired_codes(self):
        """Clean up expired login codes."""
        while self.running:
            try:
                db = SessionLocal()
                try:
                    # Delete codes older than 10 minutes
                    expired_time = datetime.utcnow() - timedelta(minutes=10)
                    expired_codes = db.query(LoginCode).filter(
                        LoginCode.created_at < expired_time
                    ).all()
                    
                    for code in expired_codes:
                        db.delete(code)
                    
                    db.commit()
                    
                    if expired_codes:
                        logger.info(f"Cleaned up {len(expired_codes)} expired login codes")
                
                finally:
                    db.close()
                
                # Run every 5 minutes
                await asyncio.sleep(300)
            
            except Exception as e:
                logger.error(f"Error in cleanup_expired_codes: {e}")
                await asyncio.sleep(60)
    
    async def cleanup_stale_sessions(self):
        """Clean up stale traffic sessions."""
        while self.running:
            try:
                db = SessionLocal()
                try:
                    # Find sessions that haven't been updated in 1 hour
                    stale_time = datetime.utcnow() - timedelta(hours=1)
                    stale_sessions = db.query(TrafficSession).filter(
                        TrafficSession.status == SessionStatus.ACTIVE,
                        TrafficSession.updated_at < stale_time
                    ).all()
                    
                    for session in stale_sessions:
                        session.status = SessionStatus.COMPLETED
                        session.ended_at = datetime.utcnow()
                    
                    db.commit()
                    
                    if stale_sessions:
                        logger.info(f"Cleaned up {len(stale_sessions)} stale sessions")
                
                finally:
                    db.close()
                
                # Run every 30 minutes
                await asyncio.sleep(1800)
            
            except Exception as e:
                logger.error(f"Error in cleanup_stale_sessions: {e}")
                await asyncio.sleep(300)
    
    async def process_payments(self):
        """Process pending payments."""
        while self.running:
            try:
                db = SessionLocal()
                try:
                    # Find pending payments older than 24 hours
                    pending_time = datetime.utcnow() - timedelta(hours=24)
                    pending_payments = db.query(Payment).filter(
                        Payment.status == PaymentStatus.PENDING,
                        Payment.created_at < pending_time
                    ).all()
                    
                    for payment in pending_payments:
                        # Mark as failed if no response from payment provider
                        payment.status = PaymentStatus.FAILED
                        payment.updated_at = datetime.utcnow()
                    
                    db.commit()
                    
                    if pending_payments:
                        logger.info(f"Processed {len(pending_payments)} pending payments")
                
                finally:
                    db.close()
                
                # Run every hour
                await asyncio.sleep(3600)
            
            except Exception as e:
                logger.error(f"Error in process_payments: {e}")
                await asyncio.sleep(1800)
    
    async def update_statistics(self):
        """Update system statistics."""
        while self.running:
            try:
                db = SessionLocal()
                try:
                    # Update user statistics
                    total_users = db.query(User).count()
                    active_users = db.query(User).filter(User.is_active == True).count()
                    
                    # Update traffic statistics
                    today = datetime.utcnow().date()
                    today_sessions = db.query(TrafficSession).filter(
                        TrafficSession.created_at >= today
                    ).all()
                    
                    total_traffic = sum(session.bytes_total for session in today_sessions)
                    active_sessions = len([s for s in today_sessions if s.status == SessionStatus.ACTIVE])
                    
                    logger.info(f"Stats - Users: {total_users}, Active: {active_users}, "
                              f"Traffic: {total_traffic / (1024**3):.2f} GB, "
                              f"Sessions: {active_sessions}")
                
                finally:
                    db.close()
                
                # Run every 10 minutes
                await asyncio.sleep(600)
            
            except Exception as e:
                logger.error(f"Error in update_statistics: {e}")
                await asyncio.sleep(300)

# Global background task manager
background_tasks = BackgroundTaskManager()
