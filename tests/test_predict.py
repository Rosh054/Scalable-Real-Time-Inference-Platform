"""Prediction endpoint tests."""

VALID_PAYLOAD = {
    "sepal_length": 5.1,
    "sepal_width": 3.5,
    "petal_length": 1.4,
    "petal_width": 0.2,
}


def test_predict_valid_request(client):
    response = client.post("/predict", json=VALID_PAYLOAD)
    assert response.status_code == 200
    data = response.json()
    assert "prediction" in data
    assert data["prediction"] in (0, 1, 2)
    assert data["model_version"]
    assert data["request_id"]
    assert data["cache_hit"] is False
    assert data["latency_ms"] >= 0


def test_predict_invalid_request(client):
    response = client.post("/predict", json={"sepal_length": -1})
    assert response.status_code == 422


def test_predict_logs_to_db(client, db_session):
    from app.db.models import Prediction

    client.post("/predict", json=VALID_PAYLOAD)
    rows = db_session.query(Prediction).all()
    assert len(rows) >= 1
    row = rows[-1]
    assert row.input_payload == VALID_PAYLOAD
    assert row.cache_hit is False


def test_predict_cache_hit(client):
    first = client.post("/predict", json=VALID_PAYLOAD).json()
    assert first["cache_hit"] is False

    second = client.post("/predict", json=VALID_PAYLOAD).json()
    assert second["cache_hit"] is True
    assert second["prediction"] == first["prediction"]
