"""
Test API routes
"""

import pytest
from fastapi.testclient import TestClient
from traffic_share.server.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Traffic Share API"
    assert data["status"] == "online"


def test_register_endpoint():
    """Test user registration endpoint"""
    response = client.post("/api/auth/register", json={
        "telegram_id": 123456789,
        "username": "testuser"
    })
    assert response.status_code == 200
    data = response.json()
    assert "user_id" in data


def test_invalid_register():
    """Test invalid registration"""
    response = client.post("/api/auth/register", json={
        "telegram_id": "invalid"
    })
    assert response.status_code == 422


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
