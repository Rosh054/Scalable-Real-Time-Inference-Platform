"""Metrics endpoint tests."""


def test_metrics_endpoint(client):
    client.post(
        "/predict",
        json={
            "sepal_length": 5.1,
            "sepal_width": 3.5,
            "petal_length": 1.4,
            "petal_width": 0.2,
        },
    )
    response = client.get("/metrics")
    assert response.status_code == 200
    text = response.text
    assert "inference_predictions_total" in text
    assert "inference_cache_hit_rate" in text
