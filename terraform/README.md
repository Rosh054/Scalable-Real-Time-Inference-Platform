# AWS Terraform Deployment

Infrastructure for the scalable real-time inference platform.

**Amazon SDE reviewers:** You do not need `terraform apply` to assess this project. Run `../scripts/verify_terraform.sh` or see [../docs/VERIFICATION.md](../docs/VERIFICATION.md).

## Resources created

- VPC (public + private subnets, NAT)
- ECR repository
- ECS Fargate cluster, task definition, service (with CPU autoscaling)
- Application Load Balancer + target group
- RDS PostgreSQL (`db.t3.micro`)
- ElastiCache Redis (`cache.t3.micro`)
- S3 bucket for model artifacts
- CloudWatch log group, dashboard, alarms (5xx, latency, CPU, unhealthy tasks)
- IAM roles for ECS execution and S3 model read

## Prerequisites

- [Terraform](https://www.terraform.io/downloads) >= 1.5
- AWS CLI configured (`aws configure`)
- Docker (to build and push the API image)

## Deploy

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars

terraform init
terraform plan
terraform apply
```

## Upload model to S3

```bash
cd ..
make train-model
aws s3 cp models/model.joblib s3://$(terraform -chdir=terraform output -raw s3_model_bucket)/models/model.joblib
```

## Push Docker image to ECR

```bash
ECR_URL=$(terraform -chdir=terraform output -raw ecr_repository_url)
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin ${ECR_URL%%/*}
docker build -t $ECR_URL:latest ..
docker push $ECR_URL:latest

# Update ECS to use the new image
aws ecs update-service \
  --cluster $(terraform -chdir=terraform output -raw ecs_cluster_name) \
  --service $(terraform -chdir=terraform output -raw ecs_service_name) \
  --force-new-deployment
```

## Test ALB

```bash
ALB=$(terraform -chdir=terraform output -raw alb_dns_name)
curl "http://$ALB/health"
curl -X POST "http://$ALB/predict" \
  -H "Content-Type: application/json" \
  -d '{"sepal_length":5.1,"sepal_width":3.5,"petal_length":1.4,"petal_width":0.2}'
```

## Teardown (avoid ongoing charges)

```bash
cd terraform
terraform destroy
```

Confirm destruction of RDS, ElastiCache, NAT Gateway, and ALB. Empty the S3 bucket first if `force_delete` is not set on the bucket.

## Cost warning

Running this stack incurs AWS charges (NAT Gateway, RDS, ElastiCache, Fargate, ALB). Use `terraform destroy` when finished. Estimated dev cost: roughly **$50–150/month** depending on usage and region.

## Production hardening (not in scope)

- Store `DATABASE_URL` in AWS Secrets Manager
- HTTPS on ALB (ACM certificate)
- Multi-AZ RDS and Redis replication
- Private ECR image scanning policies
- WAF on ALB

## GitHub Actions deploy secrets

| Secret | Description |
|--------|-------------|
| `AWS_ACCESS_KEY_ID` | IAM user/role access key |
| `AWS_SECRET_ACCESS_KEY` | IAM secret |

Update `.github/workflows/deploy.yml` env vars to match Terraform resource names.
