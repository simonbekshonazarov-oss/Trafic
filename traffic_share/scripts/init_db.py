"""
Initialize database - create all tables
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from traffic_share.server.database import init_db, engine
from traffic_share.server.logger import logger


def main():
    """Initialize database"""
    try:
        logger.info("Initializing database...")
        
        init_db()
        
        logger.info("Database initialized successfully!")
        logger.info(f"Database URL: {engine.url}")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
