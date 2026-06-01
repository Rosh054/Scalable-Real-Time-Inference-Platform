"""Prediction endpoint."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.schemas import PredictRequest, PredictResponse
from app.core.metrics import app_metrics
from app.db.session import get_db
from app.services.prediction_service import run_prediction

router = APIRouter(tags=["predict"])


@router.post("/predict", response_model=PredictResponse)
def predict(
    request: PredictRequest,
    db: Session = Depends(get_db),
) -> PredictResponse:
    app_metrics.record_request()
    return run_prediction(db, request)
