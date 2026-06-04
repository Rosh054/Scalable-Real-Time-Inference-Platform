# Verification Guide (for recruiters & interviewers)

This document explains how to **authenticate** project claims without trusting README text alone.

## Quick verification ($0, ~2 minutes)

**Prerequisites:** Docker running

```bash
git clone https://github.com/Rosh054/Scalable-Real-Time-Inference-Platform.git
cd Scalable-Real-Time-Inference-Platform
make setup && source .venv/bin/activate
make train-model
make up
./scripts/verify_local.sh
```

Expected: all lines print `PASS:`.

## Load test claims

| Claim | Evidence file |
|-------|----------------|
| ~713 req/s, p95 ~108 ms | `results/hey_20260601_143951.txt` |
| Summary in readable form | `results/metrics_template.md` |

Reproduce (optional):

```bash
brew install hey
make load-test
```

Compare new `results/hey_*.txt` to committed artifacts (numbers will vary slightly by machine).

## Test suite

```bash
docker compose up postgres redis -d
docker compose exec postgres psql -U inference -c "CREATE DATABASE inference_test;" 2>/dev/null || true
export TEST_DATABASE_URL=postgresql://inference:inference@localhost:5432/inference_test
export TEST_REDIS_URL=redis://localhost:6379/0
make test
```

## Terraform / AWS design (no spend)

```bash
./scripts/verify_terraform.sh
```

Validates formatting and HCL without `terraform apply`.

GitHub Actions also runs `terraform validate` on push (see `.github/workflows/terraform.yml`).

## CI authenticity

Workflow: `.github/workflows/ci.yml`

- Trains model
- Runs `ruff` + `pytest` with real Postgres + Redis service containers
- Builds Docker image

## What is NOT claimed without AWS apply

- Live ALB URL
- Production ECS metrics
- AWS load test section in `metrics_template.md` (intentionally empty unless deployed)

## Contact / reproducibility

If numbers differ on your machine, that is expected for local load tests. The methodology (hey, 50 concurrent, 30s, fixed JSON payload) is what matters.
