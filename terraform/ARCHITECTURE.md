# Terraform Module Layout

See [../docs/AWS_ARCHITECTURE.md](../docs/AWS_ARCHITECTURE.md) for the full system design.

## File map

| File | AWS resources |
|------|----------------|
| `vpc.tf` | VPC, subnets, IGW, NAT, route tables |
| `security_groups.tf` | ALB, ECS, RDS, Redis security groups |
| `alb.tf` | ALB, target group, listener |
| `ecs.tf` | ECS cluster, task definition, service, autoscaling |
| `ecr.tf` | ECR repository |
| `rds.tf` | RDS PostgreSQL |
| `elasticache.tf` | ElastiCache Redis |
| `s3.tf` | Model artifacts bucket |
| `iam.tf` | ECS execution + task roles, CloudWatch log group |
| `cloudwatch.tf` | Dashboard, SNS, alarms |

## Interview notes

- ECS tasks run in **private subnets** without public IPs.
- ALB is the only internet-facing entry on port 80.
- Task role grants **S3 GetObject** only on the model bucket.
- `DATABASE_URL` is injected via task definition (production: use Secrets Manager).

## Validate without cost

```bash
../scripts/verify_terraform.sh
```
