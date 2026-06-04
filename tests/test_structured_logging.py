"""Structured logging configuration tests."""

import json
import logging

from app.core.structured_logging import JsonFormatter, configure_logging


def test_json_formatter_outputs_parseable_json():
    configure_logging("INFO", "aws")
    logger = logging.getLogger("test.structured")
    record = logger.makeRecord(
        "test.structured",
        logging.INFO,
        __file__,
        10,
        "prediction_complete",
        (),
        None,
    )
    record.request_id = "abc-123"
    record.cache_hit = True
    record.latency_ms = 1.5
    line = JsonFormatter().format(record)
    data = json.loads(line)
    assert data["message"] == "prediction_complete"
    assert data["request_id"] == "abc-123"
    assert data["cache_hit"] is True
