"""
Seed database with test data
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from traffic_share.server.database import get_db_context
from traffic_share.server.models import User, Admin, Buyer, Package
from traffic_share.core.security import SecurityManager
from traffic_share.server.logger import logger


def seed_test_users():
    """Create test users"""
    with get_db_context() as db:
        # Create test user
        test_user = User(
            telegram_id=123456789,
            username="test_user",
            phone="+998901234567",
            balance=10.50,
            total_earned=50.00,
            is_verified=True
        )
        db.add(test_user)
        logger.info("Created test user")


def seed_admin():
    """Create admin user"""
    with get_db_context() as db:
        # Create admin
        admin = Admin(
            telegram_id=987654321,
            username="admin",
            role="superadmin"
        )
        db.add(admin)
        logger.info("Created admin user")


def seed_buyer():
    """Create test buyer"""
    with get_db_context() as db:
        # Create buyer
        buyer = Buyer(
            name="Test Buyer",
            contact="buyer@example.com",
            region="US"
        )
        db.add(buyer)
        db.flush()
        
        # Create buyer token
        from traffic_share.server.models import BuyerToken
        
        plain_token = SecurityManager.generate_api_token(32)
        token_hash = SecurityManager.hash_token(plain_token)
        
        token = BuyerToken(
            buyer_id=buyer.id,
            token_hash=token_hash,
            description="Test token"
        )
        db.add(token)
        
        logger.info(f"Created buyer with token: {plain_token}")
        print(f"\n⚠️  SAVE THIS TOKEN: {plain_token}\n")


def seed_packages():
    """Create test packages"""
    with get_db_context() as db:
        # Get first user
        user = db.query(User).first()
        if not user:
            logger.warning("No users found, skipping package creation")
            return
        
        # Create packages
        for i in range(10):
            package = Package(
                uuid=SecurityManager.generate_uuid(),
                user_id=user.id,
                ip=f"93.184.216.{i+1}",
                size_bytes=1000000 * (i + 1),
                status="available"
            )
            db.add(package)
        
        logger.info("Created 10 test packages")


def main():
    """Seed all test data"""
    try:
        logger.info("Seeding database with test data...")
        
        seed_test_users()
        seed_admin()
        seed_buyer()
        seed_packages()
        
        logger.info("Database seeded successfully!")
        
    except Exception as e:
        logger.error(f"Database seeding failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
