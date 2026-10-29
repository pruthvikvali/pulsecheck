
import os

from fastapi.testclient import TestClient

from app.main import app


os.environ["PULSECHECK_API_KEY"] = "test-pulsecheck-key"

client = TestClient(app)

AUTH_HEADERS = {
    "X-API-Key": "test-pulsecheck-key",
}


def test_home_returns_healthy_status():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_incidents_endpoint():
    response = client.get("/incidents", headers=AUTH_HEADERS)

    assert response.status_code == 200
    assert "incidents" in response.json()


def test_github_monitor_returns_expected_fields():
    response = client.get(
        "/monitor/github",
        headers=AUTH_HEADERS,
    )

    assert response.status_code == 200

    data = response.json()
    assert data["service"] == "GitHub API"
    assert "status" in data
    assert "response_time_ms" in data
