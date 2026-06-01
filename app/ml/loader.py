"""Model loading from local filesystem or S3."""

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import joblib

from app.config import Settings, get_settings

logger = logging.getLogger(__name__)

_model: Any = None
_loaded_at: datetime | None = None
_artifact_location: str = ""


def download_from_s3(settings: Settings, dest_path: Path) -> None:
    import boto3

    if not settings.model_s3_bucket:
        raise ValueError("MODEL_S3_BUCKET is required when MODEL_SOURCE=s3")

    dest_path.parent.mkdir(parents=True, exist_ok=True)
    s3 = boto3.client("s3")
    logger.info(
        "Downloading model from s3://%s/%s",
        settings.model_s3_bucket,
        settings.model_s3_key,
    )
    s3.download_file(settings.model_s3_bucket, settings.model_s3_key, str(dest_path))


def load_model(settings: Settings | None = None) -> Any:
    global _model, _loaded_at, _artifact_location

    if _model is not None:
        return _model

    settings = settings or get_settings()
    local_path = Path(settings.model_local_path)

    if settings.model_source == "s3":
        download_from_s3(settings, local_path)
        _artifact_location = f"s3://{settings.model_s3_bucket}/{settings.model_s3_key}"
    else:
        if not local_path.exists():
            raise FileNotFoundError(f"Model not found at {local_path}. Run: make train-model")
        _artifact_location = str(local_path.resolve())

    _model = joblib.load(local_path)
    _loaded_at = datetime.now(timezone.utc)
    logger.info("Model loaded from %s", _artifact_location)
    return _model


def get_model() -> Any:
    if _model is None:
        return load_model()
    return _model


def is_model_loaded() -> bool:
    return _model is not None


def get_loaded_at() -> datetime | None:
    return _loaded_at


def get_artifact_location() -> str:
    return _artifact_location


def reset_model_state() -> None:
    """Reset model state (for tests)."""
    global _model, _loaded_at, _artifact_location
    _model = None
    _loaded_at = None
    _artifact_location = ""
