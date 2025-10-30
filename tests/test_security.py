"""
Test security functions
"""

import pytest
from traffic_share.core.security import SecurityManager


def test_password_hashing():
    """Test password hashing"""
    security = SecurityManager("test-secret-key")
    
    password = "testpassword123"
    hashed = security.hash_password(password)
    
    assert hashed != password
    assert security.verify_password(password, hashed)
    assert not security.verify_password("wrongpassword", hashed)


def test_token_generation():
    """Test JWT token generation"""
    security = SecurityManager("test-secret-key")
    
    data = {"user_id": 123, "telegram_id": 456}
    token = security.create_access_token(data)
    
    assert token is not None
    assert isinstance(token, str)
    
    # Decode token
    decoded = security.decode_token(token)
    assert decoded["user_id"] == 123
    assert decoded["telegram_id"] == 456


def test_random_code_generation():
    """Test random code generation"""
    security = SecurityManager("test-secret-key")
    
    code = security.generate_random_code(6)
    
    assert len(code) == 6
    assert code.isdigit()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
