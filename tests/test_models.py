"""
Test database models
"""

import pytest
from datetime import datetime
from traffic_share.server.models import (
    User, Admin, LoginCode, Device, TrafficSession,
    Buyer, Package, Payment, Notification, SystemMetric
)


def test_user_creation(test_db):
    """Test User model creation"""
    user = User(
        telegram_id=123456789,
        username="testuser",
        phone="+998901234567"
    )
    test_db.add(user)
    test_db.commit()
    
    assert user.id is not None
    assert user.telegram_id == 123456789
    assert user.balance == 0.0
    assert user.is_active == True


def test_login_code_creation(test_db):
    """Test LoginCode model"""
    user = User(telegram_id=123456789)
    test_db.add(user)
    test_db.commit()
    
    login_code = LoginCode(
        user_id=user.id,
        code="123456",
        expires_at=datetime.utcnow()
    )
    test_db.add(login_code)
    test_db.commit()
    
    assert login_code.id is not None
    assert login_code.code == "123456"
    assert login_code.is_used == False


def test_traffic_session_properties(test_db):
    """Test TrafficSession model properties"""
    user = User(telegram_id=123456789)
    test_db.add(user)
    test_db.commit()
    
    device = Device(
        user_id=user.id,
        device_id="test-device-123"
    )
    test_db.add(device)
    test_db.commit()
    
    session = TrafficSession(
        user_id=user.id,
        device_id=device.id,
        session_uuid="test-session-123",
        total_bytes=1000000
    )
    test_db.add(session)
    test_db.commit()
    
    assert session.bytes_total == 1000000
    assert session.start_time is not None


def test_notification_creation(test_db):
    """Test Notification model"""
    notification = Notification(
        title="Test",
        message="Test message",
        notification_type="info"
    )
    test_db.add(notification)
    test_db.commit()
    
    assert notification.id is not None
    assert notification.sent_via_bot == False
    assert notification.is_read == False


def test_system_metric_creation(test_db):
    """Test SystemMetric model"""
    metric = SystemMetric(
        metric_name="test_metric",
        metric_value=100.0,
        metric_unit="count"
    )
    test_db.add(metric)
    test_db.commit()
    
    assert metric.id is not None
    assert metric.metric_name == "test_metric"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
