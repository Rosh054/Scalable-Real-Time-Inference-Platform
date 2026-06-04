# Metrics (Verifiable Artifacts)

Record real numbers from `scripts/load_test_hey.sh` or `scripts/load_test_locust.py`.
Do not invent values — run load tests against a running stack and paste results here.

**For Amazon SDE reviewers:** Reproduce with `make up && make load-test`, or inspect committed `results/hey_*.txt`.
See [docs/VERIFICATION.md](../docs/VERIFICATION.md).

## Local load test

- Date: 2026-06-01
- Tool (hey / locust): hey
- Concurrency: 50
- Duration: 30s
- Requests/sec sustained: 713.18
- p50 latency: 65.9ms
- p95 latency: 107.7ms
- p99 latency: 151.3 ms
- Error rate: 0%
- Cache hit rate (from `/metrics`): 99.94%
- Cached latency (approx): 3.296ms
- Uncached latency (approx): 19.56ms
- Latency reduction from caching: 83%

## AWS load test

> Not deployed (cost). Terraform IaC in `terraform/` validated via `make verify-terraform` and GitHub Actions.
> Fill this section only after a real `terraform apply` + ALB load test.

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
