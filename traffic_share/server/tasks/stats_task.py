"""
Statistics task - collect and aggregate system statistics
"""

import asyncio
from datetime import datetime, timedelta
from sqlalchemy import func

from traffic_share.server.database import get_db_context
from traffic_share.server.models import (
    User, TrafficSession, Payment, Package, SystemMetric
)
from traffic_share.server.utils import record_metric, bytes_to_gb
from traffic_share.server.config import settings
from traffic_share.server.logger import logger


def collect_user_stats():
    """Collect user statistics"""
    with get_db_context() as db:
        try:
            # Total users
            total_users = db.query(func.count(User.id)).scalar()
            record_metric(db, "users_total", total_users, "count")
            
            # Active users (logged in last 24h)
            day_ago = datetime.utcnow() - timedelta(days=1)
            active_users = db.query(func.count(User.id)).filter(
                User.last_login_at >= day_ago
            ).scalar()
            record_metric(db, "users_active_24h", active_users or 0, "count")
            
            # Verified users
            verified_users = db.query(func.count(User.id)).filter(
                User.is_verified == True
            ).scalar()
            record_metric(db, "users_verified", verified_users or 0, "count")
            
            logger.info(f"User stats collected: {total_users} total, {active_users} active")
            
        except Exception as e:
            logger.error(f"Error collecting user stats: {e}")


def collect_traffic_stats():
    """Collect traffic statistics"""
    with get_db_context() as db:
        try:
            # Active sessions
            active_sessions = db.query(func.count(TrafficSession.id)).filter(
                TrafficSession.status == "active"
            ).scalar()
            record_metric(db, "traffic_sessions_active", active_sessions or 0, "count")
            
            # Today's traffic
            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_stats = db.query(
                func.sum(TrafficSession.bytes_total).label("bytes"),
                func.sum(TrafficSession.earnings).label("earnings")
            ).filter(
                TrafficSession.start_time >= today
            ).first()
            
            today_gb = bytes_to_gb(today_stats.bytes or 0)
            today_earnings = today_stats.earnings or 0.0
            
            record_metric(db, "traffic_daily_gb", today_gb, "GB")
            record_metric(db, "earnings_daily_usd", today_earnings, "USD")
            
            # Total traffic
            total_stats = db.query(
                func.sum(TrafficSession.bytes_total).label("bytes"),
                func.sum(TrafficSession.earnings).label("earnings")
            ).first()
            
            total_gb = bytes_to_gb(total_stats.bytes or 0)
            total_earnings = total_stats.earnings or 0.0
            
            record_metric(db, "traffic_total_gb", total_gb, "GB")
            record_metric(db, "earnings_total_usd", total_earnings, "USD")
            
            logger.info(f"Traffic stats: {active_sessions} active, {today_gb:.2f} GB today")
            
        except Exception as e:
            logger.error(f"Error collecting traffic stats: {e}")


def collect_payment_stats():
    """Collect payment statistics"""
    with get_db_context() as db:
        try:
            # Pending payments
            pending_payments = db.query(func.count(Payment.id)).filter(
                Payment.status.in_(["pending", "processing"])
            ).scalar()
            record_metric(db, "payments_pending", pending_payments or 0, "count")
            
            # Completed today
            today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            today_payments = db.query(
                func.count(Payment.id),
                func.sum(Payment.amount)
            ).filter(
                Payment.status == "completed",
                Payment.completed_at >= today
            ).first()
            
            record_metric(db, "payments_daily_count", today_payments[0] or 0, "count")
            record_metric(db, "payments_daily_amount", today_payments[1] or 0, "USD")
            
            logger.info(f"Payment stats: {pending_payments} pending")
            
        except Exception as e:
            logger.error(f"Error collecting payment stats: {e}")


def collect_package_stats():
    """Collect package statistics"""
    with get_db_context() as db:
        try:
            # Available packages
            available = db.query(func.count(Package.id)).filter(
                Package.status == "available"
            ).scalar()
            record_metric(db, "packages_available", available or 0, "count")
            
            # Allocated packages
            allocated = db.query(func.count(Package.id)).filter(
                Package.status == "allocated"
            ).scalar()
            record_metric(db, "packages_allocated", allocated or 0, "count")
            
            # In progress
            in_progress = db.query(func.count(Package.id)).filter(
                Package.status == "in_progress"
            ).scalar()
            record_metric(db, "packages_in_progress", in_progress or 0, "count")
            
            logger.info(f"Package stats: {available} available, {allocated} allocated")
            
        except Exception as e:
            logger.error(f"Error collecting package stats: {e}")


async def run_stats_collection():
    """Run all statistics collection"""
    logger.info("Collecting system statistics...")
    
    collect_user_stats()
    collect_traffic_stats()
    collect_payment_stats()
    collect_package_stats()
    
    logger.info("Statistics collection completed")


async def stats_task_loop():
    """Periodic stats collection loop"""
    while True:
        try:
            await run_stats_collection()
        except Exception as e:
            logger.error(f"Stats task error: {e}")
        
        # Sleep for configured interval (default 1 hour)
        await asyncio.sleep(settings.STATS_TASK_INTERVAL)


if __name__ == "__main__":
    asyncio.run(run_stats_collection())
