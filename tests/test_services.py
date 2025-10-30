"""
Test service layer
"""

import pytest
from datetime import datetime, timedelta
from traffic_share.server.services.auth_service import AuthService
from traffic_share.server.schemas import RegisterRequest
from traffic_share.server.models import User, LoginCode


def test_auth_service_register_new_user(test_db):
    """Test user registration"""
    service = AuthService(test_db)
    
    request = RegisterRequest(
        telegram_id=123456789,
        username="testuser"
    )
    
    user = service.register_user(request)
    
    assert user.id is not None
    assert user.telegram_id == 123456789
    assert user.username == "testuser"


def test_auth_service_register_existing_user(test_db):
    """Test updating existing user"""
    service = AuthService(test_db)
    
    # Create user first time
    request1 = RegisterRequest(
        telegram_id=123456789,
        username="testuser"
    )
    user1 = service.register_user(request1)
    
    # Update same user
    request2 = RegisterRequest(
        telegram_id=123456789,
        username="newusername"
    )
    user2 = service.register_user(request2)
    
    assert user1.id == user2.id
    assert user2.username == "newusername"


def test_generate_login_code(test_db):
    """Test login code generation"""
    service = AuthService(test_db)
    
    # Create user first
    user = User(telegram_id=123456789)
    test_db.add(user)
    test_db.commit()
    
    # Generate code
    user, code = service.generate_login_code(123456789)
    
    assert code is not None
    assert len(code) == 6
    assert code.isdigit()
    
    # Check code in database
    login_code = test_db.query(LoginCode).filter_by(user_id=user.id).first()
    assert login_code is not None
    assert login_code.code == code


def test_verify_login_code(test_db):
    """Test login code verification"""
    service = AuthService(test_db)
    
    # Create user and code
    user = User(telegram_id=123456789)
    test_db.add(user)
    test_db.commit()
    
    code = "123456"
    login_code = LoginCode(
        user_id=user.id,
        code=code,
        expires_at=datetime.utcnow() + timedelta(hours=1)
    )
    test_db.add(login_code)
    test_db.commit()
    
    # Verify code
    tokens = service.verify_login_code(123456789, code)
    
    assert tokens.access_token is not None
    assert tokens.refresh_token is not None
    assert tokens.expires_in > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
