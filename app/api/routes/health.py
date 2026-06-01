"""Health check endpoint."""

from fastapi import APIRouter

from app.api.schemas import HealthResponse
from app.core import cache as cache_module
from app.db.session import check_db_connection
from app.ml.loader import is_model_loaded

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    redis_ok = cache_module.check_redis_connection()
    db_ok = check_db_connection()
    model_ok = is_model_loaded()

    all_ok = redis_ok and db_ok and model_ok
    return HealthResponse(
        status="healthy" if all_ok else "degraded",
        api="up",
        redis="up" if redis_ok else "down",
        database="up" if db_ok else "down",
        model="loaded" if model_ok else "not_loaded",
    )
