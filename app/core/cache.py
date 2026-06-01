"""Redis cache-aside helpers."""

import hashlib
import json
from typing import Any

import redis

from app.config import get_settings

_redis_client: redis.Redis | None = None


def get_redis() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        settings = get_settings()
        _redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    return _redis_client


def reset_redis_client() -> None:
    """Reset client (for tests)."""
    global _redis_client
    _redis_client = None


def check_redis_connection() -> bool:
    try:
        return bool(get_redis().ping())
    except Exception:
        return False


def normalize_payload(payload: dict[str, Any]) -> str:
    """Deterministic JSON for hashing."""
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def input_hash(payload: dict[str, Any]) -> str:
    normalized = normalize_payload(payload)
    return hashlib.sha256(normalized.encode()).hexdigest()


def cache_key(input_hash_value: str) -> str:
    settings = get_settings()
    return f"pred:{settings.model_version}:{input_hash_value}"


def get_cached_prediction(input_hash_value: str) -> dict[str, Any] | None:
    raw = get_redis().get(cache_key(input_hash_value))
    if raw is None:
        return None
    return json.loads(raw)


def set_cached_prediction(input_hash_value: str, data: dict[str, Any]) -> None:
    settings = get_settings()
    get_redis().setex(
        cache_key(input_hash_value),
        settings.cache_ttl_seconds,
        json.dumps(data),
    )
