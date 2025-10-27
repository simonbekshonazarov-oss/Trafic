"""
Export statistics to CSV
"""

import sys
import csv
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from traffic_share.server.database import get_db_context
from traffic_share.server.models import User, TrafficSession, Payment
from traffic_share.server.logger import logger
from traffic_share.server.utils import bytes_to_gb


def export_user_stats(output_file: str = "user_stats.csv"):
    """Export user statistics to CSV"""
    with get_db_context() as db:
        users = db.query(User).all()
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'User ID', 'Telegram ID', 'Username',
                'Balance', 'Total Earned', 'Is Active',
                'Created At'
            ])
            
            for user in users:
                writer.writerow([
                    user.id, user.telegram_id, user.username,
                    user.balance, user.total_earned, user.is_active,
                    user.created_at
                ])
        
        logger.info(f"Exported {len(users)} users to {output_file}")


def export_traffic_stats(output_file: str = "traffic_stats.csv"):
    """Export traffic statistics to CSV"""
    with get_db_context() as db:
        sessions = db.query(TrafficSession).all()
        
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Session ID', 'User ID', 'Start Time', 'End Time',
                'Total GB', 'Earnings', 'Status'
            ])
            
            for session in sessions:
                writer.writerow([
                    session.session_id, session.user_id,
                    session.start_time, session.end_time,
                    bytes_to_gb(session.bytes_total),
                    session.earnings, session.status
                ])
        
        logger.info(f"Exported {len(sessions)} sessions to {output_file}")


def main():
    """Main function"""
    try:
        logger.info("Exporting statistics...")
        
        export_user_stats()
        export_traffic_stats()
        
        logger.info("Export completed!")
        
    except Exception as e:
        logger.error(f"Export failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
