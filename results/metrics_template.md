# Metrics

Record real numbers from `scripts/load_test_hey.sh` or `scripts/load_test_locust.py`.
Do not invent values — run load tests against a running stack and paste results here.

## Local load test

- Date:
- Tool (hey / locust):
- Concurrency:
- Duration:
- Requests/sec sustained:
- p50 latency:
- p95 latency:
- p99 latency:
- Error rate:
- Cache hit rate (from `/metrics`):
- Cached latency (approx):
- Uncached latency (approx):
- Latency reduction from caching:

## AWS load test

- ALB URL:
- ECS task count:
- Requests/sec sustained:
- p95 latency:
- Error rate:
- Auto-scale range:
- CI/CD deploy time:

## Notes

- hey output file: `results/hey_*.txt`
- locust CSV: `results/locust_*`
