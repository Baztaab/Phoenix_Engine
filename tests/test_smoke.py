
from phoenix_engine.api.app import app
from fastapi.testclient import TestClient


client = TestClient(app)


def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "Phoenix" in data["engine"]


def test_calculation_import():
    # Ensure core logic imports without crashing
    from phoenix_engine.engines.birth import BirthChartEngine as VedicChart
    assert VedicChart


def test_invalid_lat_lon_rejected():
    bad = {
        "year": 1997,
        "month": 6,
        "day": 7,
        "hour": 20,
        "minute": 28,
        "timezone": "Asia/Tehran",
        "lat": 999,
        "lon": 999,
        "name": "Mehran",
    }
    response = client.post("/calculate", json=bad)
    assert response.status_code == 422
