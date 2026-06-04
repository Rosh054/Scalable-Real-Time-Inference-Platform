# Scalable Real-Time Inference Platform

A production-oriented machine learning inference platform that delivers low-latency REST API predictions with Redis caching, PostgreSQL audit logging, containerised local deployment, and Terraform-defined AWS infrastructure.

| | |
|---|---|
| **Repository** | https://github.com/Rosh054/Scalable-Real-Time-Inference-Platform |
| **Maintainer** | Roshini |
| **License** | MIT |
| **Status** | Application validated locally; AWS IaC ready (optional deploy) |

---

## Overview

This project implements an end-to-end **real-time inference service** suitable for academic, internship, and industry portfolio use. Clients submit validated feature payloads; the service returns model predictions while recording latency, cache behaviour, and a full audit trail in the database.

The same application codebase runs locally via **Docker Compose** and is designed to deploy on **Amazon Web Services** using **ECS Fargate**, **Application Load Balancer**, **RDS PostgreSQL**, **ElastiCache Redis**, **S3**, and **CloudWatch**.

**Formal documentation** (abstracts, verification, PDF): see [Documentation](#documentation) below.

---

## Key capabilities

- **REST API** — FastAPI with Pydantic validation and OpenAPI documentation (`/docs`)
- **Cache-aside (Redis)** — Deterministic input hashing; TTL-based cache with hit/miss reporting
- **Audit logging (PostgreSQL)** — Every prediction persisted with `request_id`, payload, latency, and cache status
- **Observability** — `/health`, Prometheus-style `/metrics`, structured JSON logs in AWS environments
- **Request tracing** — `X-Request-ID` on all responses for correlation with logs and database records
- **ML serving** — scikit-learn Iris classifier; local `joblib` or S3 model loading (`MODEL_SOURCE`)
- **Infrastructure as Code** — Terraform for VPC, ECS, ALB, RDS, ElastiCache, S3, IAM, CloudWatch alarms
- **CI/CD** — GitHub Actions: lint, automated tests, Docker build, compose smoke test, Terraform validate

---

## Architecture

### Production target (AWS)

```text
                    Internet
                        |
                        v
           Application Load Balancer
                        |
                        v
              ECS Fargate (FastAPI)
                 /      |       \
                v       v        v
          ElastiCache  RDS       S3
            Redis   PostgreSQL  model
                        |
                CloudWatch (logs, metrics, alarms)

        GitHub Actions  --->  ECR  --->  ECS deployment
```

### Local implementation (validated)

```text
Client  --->  FastAPI (:8000)
                 |--- Redis (cache)
                 |--- PostgreSQL (predictions)
                 v
            models/model.joblib
```

Service mapping: [docs/LOCAL_TO_AWS_MAPPING.md](docs/LOCAL_TO_AWS_MAPPING.md)

---

## Performance (verified, local)

Load tests use **hey** (50 concurrent clients, 30 seconds, fixed payload). Results are stored in the repository and must not be altered without re-running tests.

| Metric | Result |
|--------|--------|
| Throughput | ~713 requests/sec |
| Latency p50 | ~65.9 ms |
| Latency p95 | ~107.7 ms |
| Latency p99 | ~151.3 ms |
| Error rate | 0% |
| Cache hit rate (repeated payload) | ~99.9% |
| Latency reduction (cached vs uncached) | ~83% |

**Evidence:** [results/metrics_template.md](results/metrics_template.md), [results/hey_20260601_143951.txt](results/hey_20260601_143951.txt)

---

## Technology stack

| Layer | Technologies |
|-------|----------------|
| Application | Python 3.11+, FastAPI, Pydantic, Uvicorn |
| Machine learning | scikit-learn, joblib |
| Cache | Redis 7 |
| Database | PostgreSQL 15, SQLAlchemy, Alembic |
| Containers | Docker, Docker Compose |
| Cloud (IaC) | Terraform — AWS ECS, ALB, RDS, ElastiCache, S3, CloudWatch |
| Quality assurance | pytest, ruff, GitHub Actions |

---

## Getting started

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Optional: [hey](https://github.com/rakyll/hey) for load testing (`brew install hey`)

### Installation and run

```bash
git clone https://github.com/Rosh054/Scalable-Real-Time-Inference-Platform.git
cd Scalable-Real-Time-Inference-Platform

make setup
source .venv/bin/activate
make train-model
make up
```

| Endpoint | URL |
|----------|-----|
| API documentation | http://localhost:8000/docs |
| Health check | http://localhost:8000/health |

### Verification (reviewers)

```bash
make verify              # End-to-end API smoke test
make check               # Lint, pytest, Terraform validate
make verify-terraform    # IaC only (no AWS charges)
```

Full procedure: [docs/VERIFICATION.md](docs/VERIFICATION.md)

---

## API reference

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Service, Redis, database, and model status |
| `POST` | `/predict` | Run inference; returns prediction, `request_id`, `cache_hit`, `latency_ms` |
| `GET` | `/metrics` | Application counters (Prometheus text format) |
| `GET` | `/model-info` | Model metadata and input schema |

### Example: prediction request

```bash
curl -s -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "sepal_length": 5.1,
    "sepal_width": 3.5,
    "petal_length": 1.4,
    "petal_width": 0.2
  }'
```

### Example: health check

```bash
curl -s http://localhost:8000/health
```

---

## Configuration

Copy `.env.example` to `.env` for local development. Primary variables:

| Variable | Description |
|----------|-------------|
| `APP_ENV` | `local` or `aws` (controls log format) |
| `DATABASE_URL` | PostgreSQL connection string |
| `REDIS_URL` | Redis connection string |
| `MODEL_SOURCE` | `local` or `s3` |
| `MODEL_LOCAL_PATH` | Path to joblib artifact |
| `CACHE_TTL_SECONDS` | Redis entry TTL |

---

## Makefile commands

| Command | Description |
|---------|-------------|
| `make setup` | Create virtual environment and install dependencies |
| `make train-model` | Train and save Iris classifier to `models/model.joblib` |
| `make up` | Start Docker Compose stack |
| `make down` | Stop Docker Compose stack |
| `make test` | Run pytest (requires PostgreSQL and Redis) |
| `make check` | Lint, test, and Terraform validate |
| `make verify` | Automated local verification script |
| `make load-test` | Run hey load test against local API |
| `make pdf` | Generate formal PDF from project documentation |

---

## AWS deployment

Terraform under `terraform/` defines the full production stack. Deployment is **optional** and incurs AWS charges (NAT Gateway, RDS, ElastiCache, ALB, Fargate).

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform plan
terraform apply   # only when ready to incur cost
```

Teardown: `terraform destroy` — see [terraform/README.md](terraform/README.md).

**Note:** Application behaviour is validated locally. Live AWS metrics should only be claimed after a successful deploy and documented load test.

---

## CI/CD

| Workflow | Description |
|----------|-------------|
| [ci.yml](.github/workflows/ci.yml) | Ruff lint, pytest, Docker image build, Compose smoke test |
| [terraform.yml](.github/workflows/terraform.yml) | `terraform fmt` and `validate` |
| [deploy.yml](.github/workflows/deploy.yml) | Optional ECR push and ECS deploy (requires AWS secrets) |

---

## Project structure

```text
app/                 Application source (API, cache, database, ML, services)
docs/                Formal and technical documentation
terraform/           AWS infrastructure-as-code
scripts/             Training, load testing, verification, PDF generation
tests/               Automated test suite
results/             Load-test metrics and artifacts
.github/workflows/   Continuous integration and deployment
```

---

## Documentation

| Document | Audience |
|----------|----------|
| [FORMAL_PROJECT_DOCUMENTATION.md](docs/FORMAL_PROJECT_DOCUMENTATION.md) | Academic, internship, institutional enquiries |
| [DOCUMENTATION_INDEX.md](docs/DOCUMENTATION_INDEX.md) | Documentation catalogue |
| [LETTER_SUPPORT_SUMMARY.md](docs/LETTER_SUPPORT_SUMMARY.md) | One-page summary for reference letters |
| [Scalable_Real-Time_Inference_Platform_Formal_Document.pdf](docs/Scalable_Real-Time_Inference_Platform_Formal_Document.pdf) | Printable formal document |
| [VERIFICATION.md](docs/VERIFICATION.md) | Third-party reproduction guide |
| [AWS_ARCHITECTURE.md](docs/AWS_ARCHITECTURE.md) | AWS design and Well-Architected mapping |
| [ARCHITECTURE_DECISIONS.md](docs/ARCHITECTURE_DECISIONS.md) | Architecture decision records |

---

## Testing

```bash
docker compose up postgres redis -d
docker compose exec postgres psql -U inference -c "CREATE DATABASE inference_test;" 2>/dev/null || true

export TEST_DATABASE_URL=postgresql://inference:inference@localhost:5432/inference_test
export TEST_REDIS_URL=redis://localhost:6379/0
make test
```

---

## Maintenance and enquiries

This repository is maintained by **Roshini** for academic, internship, and professional reference purposes. For institutional verification, use the formal documentation and verification guide linked above.

When citing performance figures or deployment status, refer to `results/metrics_template.md` and Section 9 of the formal project documentation.

---

## License

This project is released under the [MIT License](LICENSE).
