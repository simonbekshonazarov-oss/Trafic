"""
Pytest configuration and fixtures
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from traffic_share.server.database import Base
from traffic_share.server.config import settings


@pytest.fixture(scope="session")
def test_db_engine():
    """Create test database engine"""
    # Use in-memory SQLite for tests
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture(scope="function")
def test_db(test_db_engine):
    """Create test database session"""
    TestSessionLocal = sessionmaker(bind=test_db_engine)
    session = TestSessionLocal()
    yield session
    session.close()


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "telegram_id": 123456789,
        "username": "testuser",
        "phone": "+998901234567"
    }


@pytest.fixture
def sample_login_code():
    """Sample login code"""
    return "123456"
