"""Tests for the FastAPI deployment."""
import pytest
from fastapi.testclient import TestClient
from src.api import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


def test_root_endpoint(client):
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "model_loaded" in data


def test_predict_endpoint_validation(client):
    """Test prediction endpoint input validation."""
    # Test with empty text
    response = client.post("/predict", json={"text": ""})
    assert response.status_code == 422  # Validation error
    
    # Test with missing text field
    response = client.post("/predict", json={})
    assert response.status_code == 422


def test_batch_predict_validation(client):
    """Test batch prediction endpoint validation."""
    # Test with empty list
    response = client.post("/batch_predict", json={"texts": []})
    assert response.status_code == 422
    
    # Test with missing texts field
    response = client.post("/batch_predict", json={})
    assert response.status_code == 422


# Note: Actual prediction tests require a loaded model
# These would be integration tests run after model training
