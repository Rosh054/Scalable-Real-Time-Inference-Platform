"""Model metadata endpoint."""

from fastapi import APIRouter, HTTPException

from app.api.schemas import ModelInfoResponse
from app.services.prediction_service import build_model_info

router = APIRouter(tags=["model"])


@router.get("/model-info", response_model=ModelInfoResponse)
def model_info() -> ModelInfoResponse:
    info = build_model_info()
    if not info.get("loaded"):
        raise HTTPException(status_code=503, detail="Model not loaded")
    return ModelInfoResponse(
        model_name=info["model_name"],
        model_version=info["model_version"],
        input_schema=info["input_schema"],
        artifact_location=info["artifact_location"],
        loaded_at=info["loaded_at"],
    )
