"""Pytest fixtures."""

import os
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Set test env before app imports
os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault(
    "DATABASE_URL",
    os.environ.get(
        "TEST_DATABASE_URL", "postgresql://inference:inference@localhost:5432/inference_test"
    ),
)
os.environ.setdefault("REDIS_URL", os.environ.get("TEST_REDIS_URL", "redis://localhost:6379/1"))
os.environ.setdefault("MODEL_SOURCE", "local")
os.environ.setdefault("MODEL_LOCAL_PATH", "models/model.joblib")
os.environ.setdefault("MODEL_VERSION", "test-1.0.0")
os.environ.setdefault("CACHE_TTL_SECONDS", "60")

from app.config import get_settings
from app.core import cache as cache_module
from app.core.metrics import app_metrics
from app.db.models import Base
from app.db.session import get_db
from app.main import app
from app.ml.loader import load_model, reset_model_state


@pytest.fixture(scope="session", autouse=True)
def train_model_once() -> None:
    from pathlib import Path

    from scripts.train_model import train

    path = Path("models/model.joblib")
    if not path.exists():
        train(path)


@pytest.fixture(autouse=True)
def reset_metrics() -> Generator[None, None, None]:
    with app_metrics._lock:
        app_metrics.request_count = 0
        app_metrics.prediction_count = 0
        app_metrics.cache_hit_count = 0
        app_metrics.total_latency_ms = 0.0
    yield


@pytest.fixture
def db_engine():
    settings = get_settings()
    try:
        engine = create_engine(settings.database_url, pool_pre_ping=True)
        with engine.connect() as conn:
            conn.execute(__import__("sqlalchemy").text("SELECT 1"))
    except Exception as exc:
        pytest.skip(f"PostgreSQL not available: {exc}")
        return

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture
def db_session(db_engine) -> Generator[Session, None, None]:
    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)
    session = TestingSession()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def redis_available() -> None:
    get_settings.cache_clear()
    cache_module.reset_redis_client()
    try:
        r = cache_module.get_redis()
        r.flushdb()
        if not r.ping():
            pytest.skip("Redis not available")
    except Exception as exc:
        pytest.skip(f"Redis not available: {exc}")


@pytest.fixture
def client(db_engine, redis_available, train_model_once) -> Generator[TestClient, None, None]:
    get_settings.cache_clear()
    reset_model_state()
    cache_module.reset_redis_client()

    TestingSession = sessionmaker(autocommit=False, autoflush=False, bind=db_engine)

    def override_get_db() -> Generator[Session, None, None]:
        session = TestingSession()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    load_model()
    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    reset_model_state()
    cache_module.reset_redis_client()
    try:
        cache_module.get_redis().flushdb()
    except Exception:
        pass
