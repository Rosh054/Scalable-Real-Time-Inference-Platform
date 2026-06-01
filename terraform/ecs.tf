resource "aws_ecs_cluster" "main" {
  name = "${local.name}-cluster"
  tags = local.tags

  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}

locals {
  ecr_image = var.api_image != "" ? var.api_image : "${aws_ecr_repository.api.repository_url}:latest"
  database_url = "postgresql://${var.db_username}:${random_password.db.result}@${aws_db_instance.postgres.address}:5432/${var.db_name}"
  redis_url    = "redis://${aws_elasticache_cluster.redis.cache_nodes[0].address}:6379/0"
}

resource "aws_ecs_task_definition" "api" {
  family                   = "${local.name}-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.ecs_task_execution.arn
  task_role_arn            = aws_iam_role.ecs_task.arn

  container_definitions = jsonencode([{
    name  = "api"
    image = local.ecr_image
    portMappings = [{
      containerPort = 8000
      protocol      = "tcp"
    }]
    environment = [
      { name = "APP_ENV", value = "aws" },
      { name = "DATABASE_URL", value = local.database_url },
      { name = "REDIS_URL", value = local.redis_url },
      { name = "MODEL_SOURCE", value = "s3" },
      { name = "MODEL_S3_BUCKET", value = aws_s3_bucket.models.bucket },
      { name = "MODEL_S3_KEY", value = "models/model.joblib" },
      { name = "MODEL_LOCAL_PATH", value = "/tmp/model.joblib" },
      { name = "MODEL_VERSION", value = "1.0.0" },
      { name = "CACHE_TTL_SECONDS", value = "300" },
      { name = "LOG_LEVEL", value = "INFO" },
    ]
    logConfiguration = {
      logDriver = "awslogs"
      options = {
        awslogs-group         = aws_cloudwatch_log_group.api.name
        awslogs-region        = var.aws_region
        awslogs-stream-prefix = "api"
      }
    }
    healthCheck = {
      command     = ["CMD-SHELL", "curl -f http://localhost:8000/health || exit 1"]
      interval    = 30
      timeout     = 5
      retries     = 3
      startPeriod = 60
    }
  }])

  tags = local.tags
}

resource "aws_ecs_service" "api" {
  name            = "${local.name}-service"
  cluster         = aws_ecs_cluster.main.id
  task_definition = aws_ecs_task_definition.api.arn
  desired_count   = var.desired_count
  launch_type     = "FARGATE"

  network_configuration {
    subnets          = aws_subnet.private[*].id
    security_groups  = [aws_security_group.ecs.id]
    assign_public_ip = false
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.api.arn
    container_name   = "api"
    container_port   = 8000
  }

  depends_on = [aws_lb_listener.http]

  tags = local.tags
}

resource "aws_appautoscaling_target" "ecs" {
  max_capacity       = 6
  min_capacity       = var.desired_count
  resource_id        = "service/${aws_ecs_cluster.main.name}/${aws_ecs_service.api.name}"
  scalable_dimension = "ecs:service:DesiredCount"
  service_namespace  = "ecs"
}

resource "aws_appautoscaling_policy" "cpu" {
  name               = "${local.name}-cpu-scale"
  policy_type        = "TargetTrackingScaling"
  resource_id        = aws_appautoscaling_target.ecs.resource_id
  scalable_dimension = aws_appautoscaling_target.ecs.scalable_dimension
  service_namespace  = aws_appautoscaling_target.ecs.service_namespace

  target_tracking_scaling_policy_configuration {
    predefined_metric_specification {
      predefined_metric_type = "ECSServiceAverageCPUUtilization"
    }
    target_value       = 70.0
    scale_in_cooldown  = 300
    scale_out_cooldown = 60
  }
}
