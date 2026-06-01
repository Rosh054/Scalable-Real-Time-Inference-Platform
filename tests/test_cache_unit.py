"""Unit tests for cache hashing (no Redis required)."""

from app.core.cache import input_hash, normalize_payload


def test_input_hash_is_deterministic():
    payload = {"sepal_length": 5.1, "sepal_width": 3.5, "petal_length": 1.4, "petal_width": 0.2}
    assert input_hash(payload) == input_hash(payload)


def test_input_hash_key_order_independent():
    a = {"b": 2, "a": 1}
    b = {"a": 1, "b": 2}
    assert normalize_payload(a) == normalize_payload(b)
    assert input_hash(a) == input_hash(b)
