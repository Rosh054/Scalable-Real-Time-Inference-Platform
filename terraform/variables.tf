variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Resource name prefix"
  type        = string
  default     = "inference-platform"
}

variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

variable "api_image" {
  description = "ECR image URI (set after first push or use placeholder)"
  type        = string
  default     = ""
}

variable "desired_count" {
  type    = number
  default = 2
}

variable "db_username" {
  type    = string
  default = "inference_admin"
}

variable "db_name" {
  type    = string
  default = "inference"
}

variable "alarm_email" {
  description = "Email for CloudWatch alarm SNS (optional)"
  type        = string
  default     = ""
}
