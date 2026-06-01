"""Model loading tests."""

from pathlib import Path

from app.ml.loader import get_artifact_location, is_model_loaded, load_model, reset_model_state


def test_model_loading():
    reset_model_state()
    model = load_model()
    assert model is not None
    assert is_model_loaded()
    assert Path("models/model.joblib").exists() or get_artifact_location()


def test_model_info_endpoint(client):
    response = client.get("/model-info")
    assert response.status_code == 200
    data = response.json()
    assert data["model_name"] == "iris_classifier"
    assert data["model_version"]
    assert "input_schema" in data
    assert data["loaded_at"]
