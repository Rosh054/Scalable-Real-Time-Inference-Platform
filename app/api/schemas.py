"""Pydantic request/response schemas."""

from pydantic import BaseModel, Field


class PredictRequest(BaseModel):
    sepal_length: float = Field(..., ge=0, le=30, description="Sepal length in cm")
    sepal_width: float = Field(..., ge=0, le=30, description="Sepal width in cm")
    petal_length: float = Field(..., ge=0, le=30, description="Petal length in cm")
    petal_width: float = Field(..., ge=0, le=30, description="Petal width in cm")


class PredictResponse(BaseModel):
    prediction: int
    model_version: str
    request_id: str
    cache_hit: bool
    latency_ms: float


class HealthResponse(BaseModel):
    status: str
    api: str
    redis: str
    database: str
    model: str


class ModelInfoResponse(BaseModel):
    model_name: str
    model_version: str
    input_schema: dict
    artifact_location: str
    loaded_at: str | None
