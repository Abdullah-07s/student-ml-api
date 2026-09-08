from fastapi.testclient import TestClient
from app import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "application": "student-ml-api", "version": "1.0.0"}

def test_predict_success():
    response = client.post("/predict", json={"value": 10})
    assert response.status_code == 200
    assert response.json() == {"input": 10, "prediction": 20}

def test_predict_missing_input():
    response = client.post("/predict", json={})
    assert response.status_code == 422

def test_predict_invalid_input():
    response = client.post("/predict", json={"value": "abc"})
    assert response.status_code == 422