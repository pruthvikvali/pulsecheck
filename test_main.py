
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_home_returns_healthy_status():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["service"] == "PulseCheck"


def test_incidents_endpoint():
    response = client.get("/incidents")

    assert response.status_code == 200
    assert "incidents" in response.json()
    assert isinstance(response.json()["incidents"], list)


def test_github_monitor_returns_expected_fields():
    response = client.get("/monitor/github")

    assert response.status_code == 200

    data = response.json()
    assert data["service"] == "GitHub API"
    assert data["status"] in ["up", "down"]
    assert "response_time_ms" in data
    assert "checked_at" in data
