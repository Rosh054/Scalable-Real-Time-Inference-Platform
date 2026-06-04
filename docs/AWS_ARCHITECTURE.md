# AWS Architecture

Target production topology for the inference platform (implemented in `terraform/`).

## Request flow

```text
Internet
   │
   ▼
Application Load Balancer (public subnets)
   │  HTTP :80, health check GET /health
   ▼
ECS Fargate Service (private subnets, awsvpc)
   │  Container :8000 (FastAPI)
   ├──► ElastiCache Redis :6379  (cache-aside)
   ├──► RDS PostgreSQL :5432     (predictions table)
   └──► S3 GetObject             (model.joblib at startup)

CloudWatch Logs ◄── ECS task (awslogs driver)
CloudWatch Alarms ◄── ALB 5xx, p95 latency, ECS CPU, unhealthy targets
SNS ◄── optional email on alarm
```

## CI/CD flow

```text
GitHub Actions (ci.yml)
  → pytest + ruff + Docker build

GitHub Actions (deploy.yml, optional)
  → docker build → ECR push → ECS rolling deploy
```

## Well-Architected Framework mapping

| Pillar | Implementation |
|--------|----------------|
| **Operational Excellence** | `/health`, `/metrics`, structured JSON logs on AWS, CloudWatch dashboard + alarms |
| **Security** | Private ECS/RDS/Redis subnets; security groups least-path; IAM task role for S3 only; no secrets in git |
| **Reliability** | ALB health checks; ECS desired count ≥ 2; CPU autoscaling; RDS backups (default window) |
| **Performance** | Redis cache-aside; connection pooling (SQLAlchemy); load-test evidence |
| **Cost Optimization** | Fargate right-sizing (512 CPU / 1024 MB); `terraform destroy` documented; local $0 path |
| **Sustainability** | Cache reduces repeated inference CPU |

## Security model (interview talking points)

- **Network:** ALB is only public ingress; ECS tasks have no public IP.
- **Data:** RDS and Redis accept traffic only from ECS security group.
- **Identity:** ECS task execution role pulls from ECR and writes logs; task role reads S3 model prefix only.
- **Secrets (production hardening):** `DATABASE_URL` should move to **Secrets Manager** + ECS secrets (documented in `terraform/README.md`).

## Autoscaling

- **ECS:** Target tracking on `ECSServiceAverageCPUUtilization` (70% target, 2–6 tasks).
- **ALB:** Distributes across healthy targets in target group.

## Observability

| Signal | Source |
|--------|--------|
| Request/latency SLIs | ALB `TargetResponseTime`, `HTTPCode_Target_5XX_Count` |
| App counters | `GET /metrics` (Prometheus text) |
| Logs | `/ecs/inference-platform-api` — JSON lines in `APP_ENV=aws` |
| Alarms | 5xx, p95 latency > 1s, CPU > 80%, unhealthy hosts |

## Local parity (no AWS bill)

Docker Compose runs the **same application code** with local Postgres/Redis equivalents. See [LOCAL_TO_AWS_MAPPING.md](LOCAL_TO_AWS_MAPPING.md).
