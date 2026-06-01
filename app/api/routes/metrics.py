"""Application metrics endpoint."""

from fastapi import APIRouter
from fastapi.responses import PlainTextResponse

from app.core.metrics import app_metrics

router = APIRouter(tags=["metrics"])


@router.get("/metrics")
def metrics() -> PlainTextResponse:
    app_metrics.record_request()
    return PlainTextResponse(content=app_metrics.to_prometheus_text(), media_type="text/plain")
