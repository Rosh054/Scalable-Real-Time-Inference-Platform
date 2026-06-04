# Amazon SDE Portfolio Guide

This project is structured for **Amazon SDE** interviews: backend ownership, AWS service fluency, operational rigor, and **verifiable** evidence (not hand-wavy claims).

## Elevator pitch (30 seconds)

> I built a real-time ML inference platform on FastAPI with Redis cache-aside and PostgreSQL audit logging. I load-tested it locally with reproducible artifacts (~713 req/s, ~108 ms p95, 0% errors). The repo includes production-style Terraform for ECS Fargate, ALB, RDS, ElastiCache, S3, and CloudWatch—I validated application behavior locally and IaC with `terraform validate` without requiring a paid deploy for reviewers.

## Amazon Leadership Principles (mapping)

| LP | How this project demonstrates it |
|----|----------------------------------|
| **Ownership** | End-to-end: API, cache, DB schema, Docker, IaC, CI, load tests, metrics template |
| **Dive Deep** | Cache-aside with deterministic hashing; per-request DB audit trail; p50/p95/p99 measured |
| **Deliver Results** | Working `/predict` under load; committed `results/hey_*.txt` artifacts |
| **Insist on Highest Standards** | Typed API (Pydantic), pytest, ruff, health checks, CloudWatch alarms in Terraform |
| **Learn and Be Curious** | Dual model loading (local joblib vs S3); ECS task IAM for S3 read |
| **Frugality** | `$0` reviewer path: Docker Compose + `verify_local.sh`; Terraform validate without apply |

## AWS services (what to discuss in interviews)

| AWS service | Role in this project |
|-------------|----------------------|
| **ECS Fargate** | Runs containerized FastAPI (no EC2 management) |
| **ALB** | HTTP routing, health checks on `/health`, target group |
| **ECR** | Private container registry; CI pushes image |
| **RDS PostgreSQL** | Durable `predictions` audit log |
| **ElastiCache Redis** | Low-latency cache-aside |
| **S3** | Model artifact store (`MODEL_SOURCE=s3`) |
| **CloudWatch** | Logs (JSON in AWS env), dashboard, alarms (5xx, latency, CPU, unhealthy tasks) |
| **IAM** | Task role (S3 read), execution role (ECR/logs) |
| **VPC** | Public subnets (ALB), private subnets (ECS, RDS, Redis), NAT |

## Honest positioning (important)

| Claim | Supported by |
|-------|----------------|
| "Built inference API with caching + DB logging" | Code + `make up` + `verify_local.sh` |
| "Load tested at X req/s / Y ms p95" | `results/hey_*.txt` + `metrics_template.md` |
| "Designed AWS deployment with Terraform" | `terraform/` + `verify_terraform.sh` + CI |
| "Deployed to production AWS" | Only if **you** ran `terraform apply` and can show ALB URL |

**Do not claim live AWS deploy** unless you actually applied Terraform and have ALB metrics.

## Resume bullets (verified local + AWS design)

```text
Built a FastAPI real-time ML inference service with Redis cache-aside and PostgreSQL prediction logging; load-tested locally at ~713 req/s, ~66 ms p50 / ~108 ms p95, 0% errors (artifacts in results/).
```

```text
Designed AWS deployment (ECS Fargate, ALB, RDS PostgreSQL, ElastiCache Redis, S3, CloudWatch) in Terraform with autoscaling and operational alarms; validated IaC via CI terraform validate.
```

## 5-minute live demo (interview)

```bash
make up
./scripts/verify_local.sh
curl -s http://localhost:8000/metrics | head -20
cat results/metrics_template.md
```

Then walk `terraform/ecs.tf` + `app/core/cache.py` on screen.

## Deep-dive topics Amazon likes

1. **Why cache-aside?** Read path: Redis → on miss, compute → write-through to Redis with TTL.
2. **Why hash inputs?** Stable cache keys across JSON key order (`sort_keys=True`).
3. **Why log every prediction?** Auditability, replay debugging, SLA analysis.
4. **How would you scale on AWS?** ALB + multi-AZ ECS tasks + Redis + RDS; CPU autoscaling (in Terraform).
5. **Failure modes?** Redis down → cache miss only; DB down → predict fails; model missing → 503 on `/model-info`.

## Local vs AWS deploy — which is better for Amazon?

**Winner for SDE (especially $0):** Local validation + Terraform in repo + `make verify`.

See [LOCAL_VS_AWS_FOR_AMAZON.md](LOCAL_VS_AWS_FOR_AMAZON.md) for full comparison.

## Related docs

- [AWS_ARCHITECTURE.md](AWS_ARCHITECTURE.md) — diagrams and Well-Architected mapping
- [LOCAL_TO_AWS_MAPPING.md](LOCAL_TO_AWS_MAPPING.md) — Docker Compose ↔ AWS
- [VERIFICATION.md](VERIFICATION.md) — how reviewers authenticate claims
- [ARCHITECTURE_DECISIONS.md](ARCHITECTURE_DECISIONS.md) — ADRs for interview depth
