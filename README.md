# Scalable Real-Time Inference Platform

Production-style **FastAPI** ML inference service with **Redis** cache-aside, **PostgreSQL** prediction logging, **Docker Compose** for local development, and **Terraform** + **GitHub Actions** for AWS deployment on **ECS Fargate**.

## Architecture

```text
Client
  |
  v
Application Load Balancer
  |
  v
ECS Fargate FastAPI service
  |         |          |
  v         v          v
Redis     RDS        S3 model artifacts
  |
  v
CloudWatch metrics / logs / alarms

GitHub Actions -> ECR -> ECS deployment
```

**Local (Docker Compose):**

```text
Client -> FastAPI (api) -> Redis (cache) + PostgreSQL (logs)
                |
                v
         models/model.joblib
```

## Why this project exists

Demonstrates end-to-end patterns used in real-time ML serving: validated APIs, deterministic caching, audit logging, observability hooks, containerized local dev, and cloud-native deployment (ALB, ECS, RDS, ElastiCache, S3, CloudWatch) with CI/CD.

## Features

- `GET /health` — API, Redis, DB, and model status
- `POST /predict` — Iris classification with cache-aside Redis, DB logging, latency tracking
- `GET /metrics` — Prometheus-style application counters
- `GET /model-info` — Model metadata and input schema
- Local (`MODEL_SOURCE=local`) and AWS (`MODEL_SOURCE=s3`) model loading
- Alembic migrations (optional; app also runs `create_all` on startup for local simplicity)
- Load test scripts (`hey`, Locust) with metrics template — **no fake numbers**
- Terraform for AWS + deploy workflow placeholders

## Tech stack

| Layer | Technology |
|-------|------------|
| API | FastAPI, Pydantic, Uvicorn |
| ML | scikit-learn, joblib |
| Cache | Redis |
| DB | PostgreSQL, SQLAlchemy |
| Containers | Docker, Docker Compose |
| IaC | Terraform (AWS) |
| CI/CD | GitHub Actions |
| Tests | pytest |

## Local setup

### Prerequisites

- Python 3.11+
- Docker & Docker Compose
- (Optional) `hey` for load tests: `brew install hey`

### Quick start

```bash
cd scalable-real-time-inference-platform
make setup
source .venv/bin/activate
make train-model
make up
```

API: http://localhost:8000/docs

### Without Docker (dev)

```bash
make setup && source .venv/bin/activate
make train-model
# Start Postgres + Redis (e.g. docker compose up postgres redis -d)
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

## API examples

**Health**

```bash
curl -s http://localhost:8000/health | jq
```

**Predict**

```bash
curl -s -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"sepal_length":5.1,"sepal_width":3.5,"petal_length":1.4,"petal_width":0.2}' | jq
```

**Metrics**

```bash
curl -s http://localhost:8000/metrics
```

**Model info**

```bash
curl -s http://localhost:8000/model-info | jq
```

## Load testing

Start the stack, then run:

```bash
# hey (install: brew install hey)
make load-test

# Locust
source .venv/bin/activate
locust -f scripts/load_test_locust.py --host=http://localhost:8000 \
  --headless -u 50 -r 10 -t 30s --csv=results/locust
```

Record real results in `results/metrics_template.md`.

| Metric | How to collect |
|--------|----------------|
| Requests/sec, p50/p95/p99 | `hey` or Locust output |
| Error rate | hey summary / Locust failures |
| Cache hit rate | `curl /metrics` → `inference_cache_hit_rate` |

## Metrics table (fill after load tests)

See [results/metrics_template.md](results/metrics_template.md).

## AWS deployment

1. **Terraform** — [terraform/README.md](terraform/README.md)
2. Train model locally, upload to S3
3. Build & push image to ECR
4. Configure GitHub secrets for optional deploy workflow

```bash
cd terraform && terraform init && terraform apply
make train-model
./scripts/upload_model_s3.sh $(terraform output -raw s3_model_bucket)
# Build/push Docker image (see terraform/README.md)
```

### Environment variables (AWS task)

| Variable | Purpose |
|----------|---------|
| `MODEL_SOURCE` | `s3` on AWS |
| `MODEL_S3_BUCKET` | S3 bucket name |
| `MODEL_S3_KEY` | Object key |
| `DATABASE_URL` | RDS connection string |
| `REDIS_URL` | ElastiCache endpoint |

## Cost warning & teardown

This AWS stack includes NAT Gateway, RDS, ElastiCache, ALB, and Fargate — **charges apply while running**.

```bash
cd terraform && terraform destroy
```

Empty the S3 bucket if destroy fails due to objects.

## Database migrations

- **Local/Docker:** Tables created on startup via SQLAlchemy `create_all` (simple, fast iteration).
- **Production:** Prefer `alembic upgrade head` before deploy. Tradeoff: `create_all` does not manage schema changes; Alembic does.

```bash
alembic upgrade head
```

## Makefile targets

| Command | Description |
|---------|-------------|
| `make setup` | venv + dependencies + `.env` |
| `make train-model` | Train Iris model |
| `make test` | pytest |
| `make up` | `docker compose up --build -d` |
| `make down` | Stop containers |
| `make logs` | Follow API logs |
| `make load-test` | Run hey script |
| `make docker-build` | Build images |

## Testing

Requires PostgreSQL and Redis (CI provides both; locally use Docker Compose):

```bash
docker compose up postgres redis -d
# Create test DB once:
docker compose exec postgres psql -U inference -c "CREATE DATABASE inference_test;" || true

export TEST_DATABASE_URL=postgresql://inference:inference@localhost:5432/inference_test
export TEST_REDIS_URL=redis://localhost:6379/0
make test
```

## CI/CD

- **CI** (`.github/workflows/ci.yml`): lint, test, Docker build
- **Deploy** (`.github/workflows/deploy.yml`): ECR push + ECS update (manual/secrets required)

## Resume bullet templates (fill with your real metrics)

**SDE / Backend:**

```text
Built and deployed a FastAPI-based real-time ML inference service on AWS ECS Fargate with Redis caching, PostgreSQL prediction logging, and GitHub Actions CI/CD, sustaining ___ requests/sec with ___ ms p95 latency.
```

**Solutions Architect:**

```text
Designed and implemented a highly available inference platform on AWS (ECS Fargate, ALB, RDS PostgreSQL, ElastiCache Redis, S3, CloudWatch) with Terraform IaC, autoscaling, and operational alarms for latency, errors, and unhealthy targets.
```

## Project structure

```text
app/                 # FastAPI application
  api/routes/        # Endpoints
  core/              # Cache, metrics
  db/                # SQLAlchemy models
  ml/                # Model load & predict
  services/          # Prediction orchestration
scripts/             # train, load test, S3 upload
tests/               # pytest suite
terraform/           # AWS IaC
.github/workflows/   # CI/CD
results/             # Metrics template (your numbers)
```

## License

MIT — see [LICENSE](LICENSE).
