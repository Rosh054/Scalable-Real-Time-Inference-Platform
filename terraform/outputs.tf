output "alb_dns_name" {
  description = "Application Load Balancer DNS name"
  value       = aws_lb.main.dns_name
}

output "ecr_repository_url" {
  value = aws_ecr_repository.api.repository_url
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  value = aws_ecs_service.api.name
}

output "ecs_task_definition_family" {
  value = aws_ecs_task_definition.api.family
}

output "s3_model_bucket" {
  value = aws_s3_bucket.models.bucket
}

output "rds_endpoint" {
  value = aws_db_instance.postgres.address
}

output "redis_endpoint" {
  value = aws_elasticache_cluster.redis.cache_nodes[0].address
}

output "cloudwatch_log_group" {
  value = aws_cloudwatch_log_group.api.name
}

output "cloudwatch_dashboard_name" {
  value = aws_cloudwatch_dashboard.main.dashboard_name
}

output "database_url" {
  description = "Sensitive — store in Secrets Manager for production"
  value       = local.database_url
  sensitive   = true
}
