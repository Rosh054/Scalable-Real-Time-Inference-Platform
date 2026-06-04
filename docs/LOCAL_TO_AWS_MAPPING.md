# Local Docker Compose ↔ AWS Service Mapping

Use this table in Amazon interviews to explain how local validation relates to AWS.

| Concern | Local (`docker-compose.yml`) | AWS (`terraform/`) |
|---------|------------------------------|---------------------|
| Compute | `api` container | **ECS Fargate** service |
| Load balancing | `localhost:8000` | **Application Load Balancer** |
| Cache | `redis:7` service | **ElastiCache Redis** |
| Database | `postgres:15` service | **RDS PostgreSQL** |
| Model storage | `models/model.joblib` volume | **S3** + `MODEL_SOURCE=s3` |
| Container registry | Local Docker image | **ECR** |
| Logs | `docker compose logs` | **CloudWatch Logs** |
| Metrics/alarms | `GET /metrics` | **CloudWatch** dashboard + alarms |
| Networking | Single bridge network | **VPC** public/private + NAT |
| Deploy pipeline | `make up` | **GitHub Actions** → ECR → ECS |

## Environment variables (same app, different backends)

| Variable | Local | AWS (ECS task) |
|----------|-------|----------------|
| `APP_ENV` | `local` | `aws` |
| `DATABASE_URL` | `postgresql://...@postgres:5432/...` | RDS endpoint |
| `REDIS_URL` | `redis://redis:6379/0` | ElastiCache endpoint |
| `MODEL_SOURCE` | `local` | `s3` |
| `MODEL_S3_BUCKET` | — | Terraform output |

## What reviewers can verify without AWS

```bash
make up
./scripts/verify_local.sh
./scripts/verify_terraform.sh
```

## Optional AWS deploy (costs money)

Follow `terraform/README.md` only if you choose to pay for a live demo environment.
