"""Health endpoint tests."""


def test_health_returns_status(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["api"] == "up"
    assert data["redis"] == "up"
    assert data["database"] == "up"
    assert data["model"] == "loaded"
    assert data["status"] == "healthy"
