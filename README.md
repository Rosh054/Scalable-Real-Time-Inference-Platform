# Scalable Real-Time Inference Platform

**AWS-aligned, real-time ML inference service** for Amazon SDE portfolio use: FastAPI, Redis cache-aside, PostgreSQL audit logging, Docker Compose validation, and **Terraform** for ECS Fargate + ALB + RDS + ElastiCache + S3 + CloudWatch.

> **Official documentation (academic / internship / letters):** [docs/FORMAL_PROJECT_DOCUMENTATION.md](docs/FORMAL_PROJECT_DOCUMENTATION.md) · [docs/DOCUMENTATION_INDEX.md](docs/DOCUMENTATION_INDEX.md) · [docs/LETTER_SUPPORT_SUMMARY.md](docs/LETTER_SUPPORT_SUMMARY.md)  
> **Maintainer:** Roshini — repository and formal docs maintained for future enquiries.

> **For recruiters / verifiers:** Reproduce claims in ~2 minutes with `make up && make verify` — see [docs/VERIFICATION.md](docs/VERIFICATION.md).

## Amazon SDE highlights

| Area | Evidence |
|------|----------|
| **Backend** | Typed REST API, cache-aside, DB audit trail, pytest |
| **AWS design** | Full `terraform/` stack + [AWS architecture doc](docs/AWS_ARCHITECTURE.md) |
| **Operations** | Health checks, Prometheus metrics, CloudWatch alarms (IaC) |
| **Performance** | Load-tested: **~713 req/s**, **~108 ms p95**, **0% errors** — [metrics](results/metrics_template.md), [hey artifact](results/hey_20260601_143951.txt) |
| **Authenticity** | No fabricated metrics; verification scripts + CI |

**Portfolio guide:** [docs/AMAZON_SDE_PORTFOLIO.md](docs/AMAZON_SDE_PORTFOLIO.md) (Leadership Principles mapping, interview script, resume bullets).

**$0 AWS path:** Application behavior validated locally; Terraform validated with `make verify-terraform` (no `apply` required).

## Architecture

**Target AWS:**

```text
Client → ALB → ECS Fargate (FastAPI)
                  ├── ElastiCache Redis
                  ├── RDS PostgreSQL
                  └── S3 (model.joblib)
              CloudWatch logs / metrics / alarms
GitHub Actions → ECR → ECS
```

**Local parity (Docker Compose):** same app code — [local ↔ AWS mapping](docs/LOCAL_TO_AWS_MAPPING.md).

```text
Client → FastAPI → Redis + PostgreSQL
              ↓
         models/model.joblib
```

## Quick start (reviewers)

```bash
make setup && source .venv/bin/activate
make train-model
make up
make verify          # automated PASS/FAIL checks
make verify-terraform # IaC validate, no AWS spend
```

API: http://localhost:8000/docs

## Verified resume bullets (local + AWS IaC)

```text
Built a FastAPI real-time ML inference service with Redis cache-aside and PostgreSQL prediction logging; load-tested at ~713 req/s, ~66 ms p50 / ~108 ms p95, 0% errors (results/hey_*.txt).
```

```text
Designed AWS deployment (ECS Fargate, ALB, RDS, ElastiCache, S3, CloudWatch) in Terraform with CPU autoscaling and operational alarms; validated via CI terraform validate and local Docker parity.
```

## Features

- `GET /health` — API, Redis, DB, model status (ALB health check path)
- `POST /predict` — inference + cache + DB log + `request_id`, `latency_ms`
- `GET /metrics` — Prometheus-style counters (cache hit rate, latency)
- `GET /model-info` — schema + artifact location
- `MODEL_SOURCE=local` | `s3` (ECS downloads model from S3 at startup)
- JSON structured logs when `APP_ENV=aws` (CloudWatch Logs Insights)
- Load tests: `hey`, Locust — [metrics template](results/metrics_template.md)

## Tech stack

| Layer | Technology |
|-------|------------|
| API | FastAPI, Pydantic, Uvicorn |
| ML | scikit-learn, joblib |
| Cache | Redis / ElastiCache |
| DB | PostgreSQL / RDS |
| AWS IaC | Terraform (ECS, ALB, RDS, ElastiCache, S3, CloudWatch, IAM) |
| CI/CD | GitHub Actions (test + Docker + terraform validate) |

## Local vs AWS deploy (Amazon SDE)

**Better for most Amazon SDE interviews:** this repo as-is — **local proof + Terraform design** ($0).

Live AWS deploy only helps if you will operate it and discuss it deeply. See [docs/LOCAL_VS_AWS_FOR_AMAZON.md](docs/LOCAL_VS_AWS_FOR_AMAZON.md).

## Documentation

| Doc | Purpose |
|-----|---------|
| [docs/AMAZON_SDE_PORTFOLIO.md](docs/AMAZON_SDE_PORTFOLIO.md) | Interview prep, LP mapping |
| [docs/LOCAL_VS_AWS_FOR_AMAZON.md](docs/LOCAL_VS_AWS_FOR_AMAZON.md) | **Local vs AWS — which to choose** |
| [docs/AWS_ARCHITECTURE.md](docs/AWS_ARCHITECTURE.md) | Well-Architected, security, scaling |
| [docs/LOCAL_TO_AWS_MAPPING.md](docs/LOCAL_TO_AWS_MAPPING.md) | Service mapping table |
| [docs/VERIFICATION.md](docs/VERIFICATION.md) | How to authenticate claims |
| [docs/ARCHITECTURE_DECISIONS.md](docs/ARCHITECTURE_DECISIONS.md) | ADRs |
| [terraform/README.md](terraform/README.md) | Optional paid deploy |

## API examples

```bash
curl -s http://localhost:8000/health | jq
curl -s -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"sepal_length":5.1,"sepal_width":3.5,"petal_length":1.4,"petal_width":0.2}' | jq
curl -s http://localhost:8000/metrics
```

## Load testing

```bash
make load-test   # requires: brew install hey
```

Record results in `results/metrics_template.md`. Committed artifacts in `results/hey_*.txt` support reproducibility.

## AWS deployment (optional — incurs cost)

```bash
cd terraform && terraform init && terraform apply
```

See [terraform/README.md](terraform/README.md). Use `terraform destroy` when finished.

Example least-privilege deploy policy: [iam/deploy-policy.least-privilege.example.json](iam/deploy-policy.least-privilege.example.json).

## Makefile

| Command | Description |
|---------|-------------|
| `make setup` | venv + deps |
| `make train-model` | Train Iris model |
| `make up` / `make down` | Start/stop stack |
| `make verify` | Reviewer verification script |
| `make verify-terraform` | `terraform validate` (no apply) |
| `make check` | lint + test + terraform validate |
| `make test` | pytest |
| `make load-test` | hey load test |

## CI/CD

| Workflow | Purpose |
|----------|---------|
| `ci.yml` | ruff, pytest, Docker build |
| `terraform.yml` | `terraform fmt` + `validate` |
| `deploy.yml` | Optional ECR → ECS (requires AWS secrets) |

## Project structure

```text
app/              # FastAPI (api, cache, db, ml, services)
docs/             # Amazon SDE + AWS + verification guides
terraform/        # AWS IaC
iam/              # Example deploy IAM policy
scripts/          # train, load test, verify_*.sh
results/          # metrics_template.md, hey_*.txt artifacts
tests/            # pytest
```

## License

MIT — see [LICENSE](LICENSE).
