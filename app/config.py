"""Application configuration from environment variables."""

from functools import lru_cache
from typing import Literal

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "local"
    database_url: str = "postgresql://inference:inference@localhost:5432/inference"
    redis_url: str = "redis://localhost:6379/0"
    model_source: Literal["local", "s3"] = "local"
    model_local_path: str = "models/model.joblib"
    model_s3_bucket: str = ""
    model_s3_key: str = "models/model.joblib"
    model_version: str = "1.0.0"
    cache_ttl_seconds: int = 300
    log_level: str = "INFO"
    model_name: str = "iris_classifier"


@lru_cache
def get_settings() -> Settings:
    return Settings()
