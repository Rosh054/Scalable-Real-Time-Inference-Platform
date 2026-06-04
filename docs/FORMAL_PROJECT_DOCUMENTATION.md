# Formal Project Documentation

**Project Title:** Scalable Real-Time Inference Platform on AWS  
**Repository:** `scalable-real-time-inference-platform`  
**Document Version:** 1.0  
**Last Updated:** June 2026  
**Document Owner / Maintainer:** Roshini  
**Classification:** Internal / Academic / Internship Portfolio — for official reference and future enquiries  

---

## 1. Purpose of this document

This document is the **authoritative project record** for the repository. When the project is cited in academic submissions, internship reports, recommendation letters, or employer correspondence, the maintaining team must be able to answer enquiries using this documentation and the linked artifacts in the repository.

**Maintenance responsibility:** Updates to scope, deployment status, metrics, or architecture must be reflected here by the document owner when material changes occur.

---

## 2. Executive summary

The **Scalable Real-Time Inference Platform** is a production-style **machine learning inference service** that exposes a REST API for real-time predictions. The system implements:

- Low-latency **POST /predict** with validated inputs  
- **Redis** cache-aside for repeated requests  
- **PostgreSQL** logging of every prediction for audit and analysis  
- Application **health** and **metrics** endpoints  
- **Docker Compose** for full local operation  
- **Terraform** infrastructure-as-code for a target **AWS** deployment (ECS Fargate, ALB, RDS, ElastiCache, S3, CloudWatch)  
- **GitHub Actions** CI/CD for automated test, lint, Docker build, and Terraform validation  

**Validation status (as of last update):** Application behaviour and performance are **verified locally** with reproducible load-test artifacts. AWS cloud resources are **defined in Terraform** and validated statically; **live AWS deployment is optional** and was not required for project completion due to cost control.

---

## 3. Academic project abstract

**Title:** Scalable Real-Time Inference Platform on AWS  

**Abstract:**

This project focuses on building a scalable, cloud-oriented machine learning inference platform using **FastAPI**, **Docker**, **Redis**, **PostgreSQL**, and **Amazon Web Services (AWS)** design patterns including **ECS**, **Application Load Balancer**, **RDS**, **ElastiCache**, **S3**, and **CloudWatch**. The system supports low-latency REST API predictions, deterministic caching, per-request logging, health and metrics endpoints, infrastructure-as-code, auto-scaling definitions, CI/CD pipelines, and operational monitoring alarms.

The application is implemented and load-tested in a containerised local environment that mirrors the AWS service topology. Terraform modules describe the production target architecture. Documented performance results include approximately **713 requests per second** sustained throughput, **65.9 ms p50** and **107.7 ms p95** latency, **0% error rate**, and approximately **99.9% cache hit rate** under repeated-payload load testing, with verifiable artifacts stored under `results/`.

**Keywords:** Machine learning inference, FastAPI, Redis, PostgreSQL, Docker, AWS ECS, Terraform, cache-aside, observability, CI/CD.

---

## 4. Internship abstract

**Title:** Cloud-Native Backend and Distributed Systems Internship  

**Abstract:**

This internship-focused work centres on developing **scalable backend services** using **FastAPI**, **Redis**, **PostgreSQL**, **Docker**, **AWS-aligned architecture**, and **CI/CD** workflows. The deliverable is a real-time inference API with distributed caching, structured logging, database audit trails, automated testing, and infrastructure-as-code for cloud deployment.

**Scope alignment with internship themes:**

| Internship theme | Implementation in this project |
|------------------|--------------------------------|
| REST APIs | FastAPI with Pydantic validation; OpenAPI at `/docs` |
| Distributed caching | Redis cache-aside with deterministic input hashing |
| Data persistence | PostgreSQL `predictions` table; SQLAlchemy ORM |
| Containerisation | Dockerfile; Docker Compose (api, postgres, redis) |
| Cloud deployment | Terraform for ECS Fargate, ALB, RDS, ElastiCache, S3, CloudWatch |
| Monitoring | `/metrics` (Prometheus-style); CloudWatch dashboard/alarms in IaC |
| CI/CD | GitHub Actions: lint, pytest, Docker build, smoke test, `terraform validate` |

**Note on synchronous vs asynchronous processing:** This repository implements **synchronous real-time inference** (request in → prediction out in the same HTTP call). It does **not** include a separate worker queue (e.g. Celery, SQS) in the current codebase. Batch or async extensions may be documented as future work (Section 12).

---

## 5. Problem statement and objectives

### 5.1 Problem statement

ML models are often deployed as ad-hoc scripts without standard APIs, caching, logging, or cloud-ready operations. This makes it difficult to achieve low latency under load, audit predictions, or migrate to managed cloud services.

### 5.2 Objectives

1. Provide a **validated REST API** for model inference.  
2. Reduce repeated-inference latency using **Redis caching**.  
3. Persist **every prediction** to PostgreSQL for traceability.  
4. Expose **health** and **metrics** for operations.  
5. Package the service for **Docker** and define **AWS** production infrastructure in **Terraform**.  
6. Automate quality checks through **CI/CD**.  
7. Record **reproducible load-test results** (no fabricated metrics).

---

## 6. System architecture

### 6.1 Target AWS architecture (production design)

```text
                    Internet
                        |
                        v
              Application Load Balancer
                        |
                        v
              ECS Fargate Service (FastAPI)
                 /        |         \
                v         v          v
         ElastiCache   RDS         S3
           Redis     PostgreSQL   model.joblib
                \        |         /
                 CloudWatch (logs, metrics, alarms)

GitHub Actions  --->  ECR  --->  ECS rolling deployment
```

### 6.2 Implemented local architecture (validated)

```text
Client  --->  FastAPI (port 8000)
                 |-------- Redis (cache)
                 |-------- PostgreSQL (predictions log)
                 v
            model.joblib (Iris classifier)
```

Local components map to AWS services as documented in [LOCAL_TO_AWS_MAPPING.md](LOCAL_TO_AWS_MAPPING.md).

### 6.3 Design patterns

- **Cache-aside:** Application reads Redis first; on miss, runs inference and writes to Redis with TTL.  
- **Audit logging:** Every `/predict` inserts one row into `predictions`.  
- **Configuration via environment variables:** Twelve-factor style; no secrets in source control.  
- **Request tracing:** `X-Request-ID` on all responses; correlates with DB `request_id`.

---

## 7. Technology stack

| Layer | Technology | Version / notes |
|-------|------------|-----------------|
| Language | Python | 3.11+ |
| API framework | FastAPI, Uvicorn | OpenAPI 3 |
| Validation | Pydantic | v2 |
| ML | scikit-learn, joblib | Iris RandomForest classifier |
| Cache | Redis | 7.x |
| Database | PostgreSQL | 15.x; SQLAlchemy 2.x |
| Migrations | Alembic | Optional; `create_all` on startup for local |
| Containers | Docker, Docker Compose | Multi-service stack |
| IaC | Terraform | AWS provider ~> 5.x |
| CI/CD | GitHub Actions | ci.yml, terraform.yml, deploy.yml (optional) |
| Load testing | hey, Locust | Scripts under `scripts/` |

---

## 8. Functional specification

### 8.1 API endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | API, Redis, database, and model status; includes `environment` and `version` |
| POST | `/predict` | Run inference; returns `prediction`, `model_version`, `request_id`, `cache_hit`, `latency_ms` |
| GET | `/metrics` | Prometheus-style counters: requests, predictions, cache hits, hit rate, avg latency |
| GET | `/model-info` | Model name, version, input schema, artifact path, `loaded_at` |

### 8.2 Input schema (Iris features)

| Field | Type | Valid range |
|-------|------|-------------|
| `sepal_length` | float | 0–30 |
| `sepal_width` | float | 0–30 |
| `petal_length` | float | 0–30 |
| `petal_width` | float | 0–30 |

### 8.3 Database schema (`predictions`)

| Column | Type | Description |
|--------|------|-------------|
| `id` | integer | Primary key |
| `request_id` | string | UUID per request |
| `model_version` | string | e.g. `1.0.0` |
| `input_hash` | string | SHA-256 of normalised JSON payload |
| `input_payload` | JSON | Request body |
| `prediction` | integer | Class label (0, 1, 2) |
| `cache_hit` | boolean | Whether Redis served the result |
| `latency_ms` | float | Server-side latency |
| `created_at` | timestamp | Insert time |

---

## 9. Deployment and environment status

| Environment | Status | Evidence |
|-------------|--------|----------|
| **Local (Docker Compose)** | **Deployed and tested** | `make up`, `make verify`, load tests |
| **CI (GitHub Actions)** | **Configured** | `.github/workflows/ci.yml`, `terraform.yml` |
| **AWS (live)** | **Not deployed** (optional; cost) | Terraform ready; `terraform apply` not required for completion |

**Statement for official correspondence:**  
The project **implements and validates** the full application stack locally and **designs** the AWS production stack in Terraform. Claims of **live AWS operation** must not be made unless `terraform apply` was executed and ALB metrics are recorded in `results/metrics_template.md` (AWS section).

---

## 10. Performance and test results

### 10.1 Documented load test (local)

**Source:** `results/metrics_template.md`, `results/hey_20260601_143951.txt`  
**Tool:** hey  
**Configuration:** 50 concurrent users, 30 seconds, fixed JSON payload  

| Metric | Value |
|--------|-------|
| Requests/sec (sustained) | 713.18 |
| p50 latency | 65.9 ms |
| p95 latency | 107.7 ms |
| p99 latency | 151.3 ms |
| Error rate | 0% |
| Cache hit rate | 99.94% |
| Uncached latency (approx.) | 19.56 ms |
| Cached latency (approx.) | 3.30 ms |
| Latency reduction from caching | 83% |

Additional runs may appear under `results/hey_*.txt` (e.g. `hey_20260604_081124.txt`).

### 10.2 Automated tests

- **13 pytest** cases: health, predict, cache, DB logging, metrics, model load, request ID middleware, structured logging.  
- Run: `make test` (requires PostgreSQL and Redis; see README).

### 10.3 Verification commands

| Command | Purpose |
|---------|---------|
| `make check` | Lint + pytest + Terraform validate |
| `make verify` | End-to-end API smoke test |
| `make verify-terraform` | Terraform fmt + validate (no AWS cost) |

---

## 11. Repository structure

```text
scalable-real-time-inference-platform/
├── app/                    # FastAPI application source
├── docs/                   # Formal and technical documentation
├── terraform/              # AWS infrastructure-as-code
├── scripts/                # Train model, load test, verification
├── tests/                  # pytest suite
├── results/                # metrics_template.md, hey_*.txt artifacts
├── .github/workflows/      # CI/CD pipelines
├── docker-compose.yml      # Local stack
├── Dockerfile              # API container image
├── Makefile                # Standard commands
├── README.md               # Quick start and overview
└── requirements.txt        # Python dependencies
```

**Primary documentation index:** [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)

---

## 12. Future work (not in current scope)

The following items appear in broader internship or cloud narratives but are **not implemented** in the current repository:

- Asynchronous job queues (e.g. SQS + worker consumers)  
- Batch inference pipelines  
- HTTPS/TLS on ALB with ACM certificates  
- AWS Secrets Manager for database credentials  
- Multi-AZ RDS and Redis replication  

These may be listed as extensions in academic or internship reports with clear labelling as **future enhancements**.

---

## 13. Operations and maintenance

### 13.1 Standard commands

```bash
make setup          # One-time Python environment
make train-model    # Generate models/model.joblib
make up             # Start Docker stack
make down           # Stop Docker stack
make check          # Lint, test, Terraform validate
make verify         # Smoke test (stack must be running)
make load-test      # Requires hey: brew install hey
```

### 13.2 AWS deployment (optional)

See [../terraform/README.md](../terraform/README.md).  
**Cost warning:** NAT Gateway, RDS, ElastiCache, ALB, and Fargate incur charges.  
**Teardown:** `terraform destroy` when finished.

### 13.3 Document owner responsibilities

The maintainer (Roshini) is responsible for:

1. Keeping this document aligned with repository changes.  
2. Updating `results/metrics_template.md` when new load tests are run.  
3. Updating Section 9 if AWS live deployment status changes.  
4. Answering team enquiries using this document and [VERIFICATION.md](VERIFICATION.md).

---

## 14. Enquiries and verification (for third parties)

When an institution, employer, or referee receives a letter referencing this project, the team should direct verifiers to:

1. **Repository:** https://github.com/Roshini054/scalable-real-time-inference-platform  
2. **This document** — `docs/FORMAL_PROJECT_DOCUMENTATION.md`.  
3. **Reproduction steps** — `docs/VERIFICATION.md`.  
4. **Evidence files** — `results/hey_*.txt`, `results/metrics_template.md`.

**Suggested verifier script (2–5 minutes):**

```bash
git clone https://github.com/Roshini054/scalable-real-time-inference-platform.git
cd scalable-real-time-inference-platform
make setup && source .venv/bin/activate
make train-model && make up
make verify
```

---

## 15. References and related documents

| Document | Location |
|----------|----------|
| **Formal PDF (print/submit)** | [Scalable_Real-Time_Inference_Platform_Formal_Document.pdf](Scalable_Real-Time_Inference_Platform_Formal_Document.pdf) |
| Documentation index | [DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md) |
| AWS architecture detail | [AWS_ARCHITECTURE.md](AWS_ARCHITECTURE.md) |
| Local ↔ AWS mapping | [LOCAL_TO_AWS_MAPPING.md](LOCAL_TO_AWS_MAPPING.md) |
| Verification guide | [VERIFICATION.md](VERIFICATION.md) |
| Architecture decisions | [ARCHITECTURE_DECISIONS.md](ARCHITECTURE_DECISIONS.md) |
| Amazon SDE portfolio notes | [AMAZON_SDE_PORTFOLIO.md](AMAZON_SDE_PORTFOLIO.md) |
| Local vs AWS deploy comparison | [LOCAL_VS_AWS_FOR_AMAZON.md](LOCAL_VS_AWS_FOR_AMAZON.md) |
| Metrics record | [../results/metrics_template.md](../results/metrics_template.md) |

---

## 16. Document approval record

| Role | Name | Date | Notes |
|------|------|------|-------|
| Project author / maintainer | Roshini | June 2026 | Initial formal release |
| Technical reviewer | _[To be completed]_ | | |
| Institutional approver | _[To be completed]_ | | |

---

*End of formal project documentation.*
