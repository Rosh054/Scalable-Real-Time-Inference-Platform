"""FastAPI application entrypoint."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import health, metrics, model_info, predict
from app.config import get_settings
from app.db.session import init_db
from app.ml.loader import load_model

settings = get_settings()
logging.basicConfig(level=getattr(logging, settings.log_level.upper(), logging.INFO))


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    load_model()
    logging.getLogger(__name__).info("Application started (env=%s)", settings.app_env)
    yield


app = FastAPI(
    title="Scalable Real-Time Inference Platform",
    description="Production-style ML inference API with Redis caching and PostgreSQL logging",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(health.router)
app.include_router(predict.router)
app.include_router(metrics.router)
app.include_router(model_info.router)
