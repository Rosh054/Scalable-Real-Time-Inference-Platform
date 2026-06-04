"""Prediction endpoint."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.schemas import PredictRequest, PredictResponse
from app.core.metrics import app_metrics
from app.db.session import get_db
from app.services.prediction_service import run_prediction

router = APIRouter(tags=["predict"])


@router.post("/predict", response_model=PredictResponse)
def predict(
    body: PredictRequest,
    http_request: Request,
    db: Session = Depends(get_db),
) -> PredictResponse:
    app_metrics.record_request()
    trace_id = getattr(http_request.state, "request_id", None)
    return run_prediction(db, body, request_id=trace_id)
