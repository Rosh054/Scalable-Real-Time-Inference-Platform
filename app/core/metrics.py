"""In-memory application metrics for /metrics endpoint."""

import threading
from dataclasses import dataclass, field


@dataclass
class AppMetrics:
    request_count: int = 0
    prediction_count: int = 0
    cache_hit_count: int = 0
    total_latency_ms: float = 0.0
    _lock: threading.Lock = field(default_factory=threading.Lock, repr=False)

    def record_request(self) -> None:
        with self._lock:
            self.request_count += 1

    def record_prediction(self, cache_hit: bool, latency_ms: float) -> None:
        with self._lock:
            self.prediction_count += 1
            if cache_hit:
                self.cache_hit_count += 1
            self.total_latency_ms += latency_ms

    @property
    def cache_hit_rate(self) -> float:
        with self._lock:
            if self.prediction_count == 0:
                return 0.0
            return self.cache_hit_count / self.prediction_count

    @property
    def average_latency_ms(self) -> float:
        with self._lock:
            if self.prediction_count == 0:
                return 0.0
            return self.total_latency_ms / self.prediction_count

    def snapshot(self) -> dict[str, float | int]:
        with self._lock:
            pred_count = self.prediction_count
            cache_hits = self.cache_hit_count
            total_lat = self.total_latency_ms
            req_count = self.request_count
        return {
            "request_count": req_count,
            "prediction_count": pred_count,
            "cache_hit_count": cache_hits,
            "cache_hit_rate": (cache_hits / pred_count) if pred_count else 0.0,
            "average_latency_ms": (total_lat / pred_count) if pred_count else 0.0,
        }

    def to_prometheus_text(self) -> str:
        s = self.snapshot()
        lines = [
            "# HELP inference_requests_total Total HTTP requests handled",
            "# TYPE inference_requests_total counter",
            f"inference_requests_total {s['request_count']}",
            "# HELP inference_predictions_total Total predictions served",
            "# TYPE inference_predictions_total counter",
            f"inference_predictions_total {s['prediction_count']}",
            "# HELP inference_cache_hits_total Total cache hits",
            "# TYPE inference_cache_hits_total counter",
            f"inference_cache_hits_total {s['cache_hit_count']}",
            "# HELP inference_cache_hit_rate Cache hit rate",
            "# TYPE inference_cache_hit_rate gauge",
            f"inference_cache_hit_rate {s['cache_hit_rate']:.6f}",
            "# HELP inference_latency_ms_avg Average prediction latency in ms",
            "# TYPE inference_latency_ms_avg gauge",
            f"inference_latency_ms_avg {s['average_latency_ms']:.4f}",
        ]
        return "\n".join(lines) + "\n"


app_metrics = AppMetrics()
