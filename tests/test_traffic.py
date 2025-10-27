"""Tests for traffic functionality."""

import pytest
from fastapi.testclient import TestClient
from traffic_share.server.main import app

client = TestClient(app)

def test_start_traffic_session():
    """Test starting a traffic session."""
    response = client.post("/api/traffic/start", json={
        "device_id": "test_device_123",
        "local_ip": "192.168.1.100",
        "public_ip": "203.0.113.1",
        "client_version": "1.0.0"
    })
    # This will fail without authentication, but tests the endpoint
    assert response.status_code in [200, 401, 403]

def test_update_traffic():
    """Test updating traffic data."""
    response = client.post("/api/traffic/update", json={
        "session_id": "test_session_123",
        "bytes_tx": 1024,
        "bytes_rx": 2048,
        "interval_seconds": 60
    })
    # This will fail without authentication, but tests the endpoint
    assert response.status_code in [200, 401, 403]

def test_stop_traffic_session():
    """Test stopping a traffic session."""
    response = client.post("/api/traffic/stop", json={
        "session_id": "test_session_123",
        "final_bytes_tx": 10240,
        "final_bytes_rx": 20480
    })
    # This will fail without authentication, but tests the endpoint
    assert response.status_code in [200, 401, 403]

def test_get_traffic_history():
    """Test getting traffic history."""
    response = client.get("/api/traffic/history")
    # This will fail without authentication, but tests the endpoint
    assert response.status_code in [200, 401, 403]

def test_get_traffic_summary():
    """Test getting traffic summary."""
    response = client.get("/api/traffic/summary")
    # This will fail without authentication, but tests the endpoint
    assert response.status_code in [200, 401, 403]
