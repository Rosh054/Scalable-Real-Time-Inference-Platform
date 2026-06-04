"""Prediction orchestration: cache, inference, persistence."""

import logging
import time
import uuid
from typing import Any

from sqlalchemy.orm import Session

from app.api.schemas import PredictRequest, PredictResponse
from app.config import get_settings
from app.core import cache as cache_module
from app.core.metrics import app_metrics
from app.db.models import Prediction
from app.ml import predictor

logger = logging.getLogger(__name__)


def run_prediction(
    db: Session,
    request: PredictRequest,
    request_id: str | None = None,
) -> PredictResponse:
    settings = get_settings()
    request_id = request_id or str(uuid.uuid4())
    payload = request.model_dump()
    hash_value = cache_module.input_hash(payload)

    start = time.perf_counter()
    cached = cache_module.get_cached_prediction(hash_value)
    cache_hit = cached is not None

    if cache_hit:
        prediction_value = int(cached["prediction"])
    else:
        prediction_value = predictor.predict(payload)
        cache_module.set_cached_prediction(
            hash_value,
            {"prediction": prediction_value, "model_version": settings.model_version},
        )

    latency_ms = (time.perf_counter() - start) * 1000

    record = Prediction(
        request_id=request_id,
        model_version=settings.model_version,
        input_hash=hash_value,
        input_payload=payload,
        prediction=prediction_value,
        cache_hit=cache_hit,
        latency_ms=latency_ms,
    )
    db.add(record)
    db.commit()

    app_metrics.record_prediction(cache_hit=cache_hit, latency_ms=latency_ms)

    logger.info(
        "prediction_complete",
        extra={
            "request_id": request_id,
            "cache_hit": cache_hit,
            "latency_ms": round(latency_ms, 3),
            "model_version": settings.model_version,
        },
    )

    return PredictResponse(
        prediction=prediction_value,
        model_version=settings.model_version,
        request_id=request_id,
        cache_hit=cache_hit,
        latency_ms=round(latency_ms, 3),
    )


def build_model_info() -> dict[str, Any]:
    from app.ml.loader import get_artifact_location, get_loaded_at, is_model_loaded

    settings = get_settings()
    loaded_at = get_loaded_at()
    return {
        "model_name": settings.model_name,
        "model_version": settings.model_version,
        "input_schema": predictor.get_input_schema(),
        "artifact_location": get_artifact_location() or settings.model_local_path,
        "loaded_at": loaded_at.isoformat() if loaded_at else None,
        "loaded": is_model_loaded(),
    }
