"""
Integration tests for FastAPI endpoints
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


def test_root_endpoint(client):
    """Test API health check"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "online"


def test_prediction_endpoint(client):
    """Test prediction endpoint"""
    request_data = {
        "time_of_day": 14,
        "day_of_week": 3,
        "location_id": 1,
        "historical_occupancy_rate": 65.5,
        "previous_duration_hours": 2.5,
        "traffic_density": "Medium"
    }
    
    response = client.post("/api/predict-availability", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "availability_probability" in data
    assert 0 <= data["availability_probability"] <= 1


def test_nearby_parkings_endpoint(client):
    """Test nearby parkings endpoint"""
    request_data = {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "radius_km": 5.0
    }
    
    response = client.post("/api/nearby-parkings", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "recommendations" in data
    assert isinstance(data["recommendations"], list)


def test_model_info_endpoint(client):
    """Test model info endpoint"""
    response = client.get("/api/model-info")
    assert response.status_code == 200
    
    data = response.json()
    assert "model_type" in data or "error" in data
