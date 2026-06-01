#!/usr/bin/env python3
"""
Locust load test for /predict endpoint.

Usage:
  locust -f scripts/load_test_locust.py --host=http://localhost:8000

Headless:
  locust -f scripts/load_test_locust.py --host=http://localhost:8000 \\
    --headless -u 50 -r 10 -t 30s --csv=results/locust
"""

import random

from locust import HttpUser, between, task


class PredictUser(HttpUser):
    wait_time = between(0.01, 0.1)

    # Fixed payload for cache hits; random for mixed workload
    CACHED_PAYLOAD = {
        "sepal_length": 5.1,
        "sepal_width": 3.5,
        "petal_length": 1.4,
        "petal_width": 0.2,
    }

    @task(weight=3)
    def predict_cached(self) -> None:
        self.client.post("/predict", json=self.CACHED_PAYLOAD)

    @task(weight=1)
    def predict_random(self) -> None:
        payload = {
            "sepal_length": round(random.uniform(4.0, 7.0), 1),
            "sepal_width": round(random.uniform(2.0, 4.5), 1),
            "petal_length": round(random.uniform(1.0, 6.5), 1),
            "petal_width": round(random.uniform(0.1, 2.5), 1),
        }
        self.client.post("/predict", json=payload)

    @task(weight=1)
    def health(self) -> None:
        self.client.get("/health")

    def on_stop(self) -> None:
        with self.client.get("/metrics", catch_response=True) as resp:
            if resp.status_code == 200:
                print("\n=== Final /metrics ===")
                print(resp.text)


if __name__ == "__main__":
    import os

    from locust.main import main

    os.environ.setdefault("LOCUST_HOST", "http://localhost:8000")
    main()
