"""Request tracing middleware tests."""


def test_predict_returns_x_request_id_header(client):
    response = client.post(
        "/predict",
        json={
            "sepal_length": 5.1,
            "sepal_width": 3.5,
            "petal_length": 1.4,
            "petal_width": 0.2,
        },
    )
    assert response.status_code == 200
    assert "X-Request-ID" in response.headers
    body = response.json()
    assert body["request_id"] == response.headers["X-Request-ID"]


def test_health_includes_environment(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "environment" in data
    assert "version" in data
