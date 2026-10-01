variable "aws_region" {
  description = "AWS deployment region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Deployment environment name"
  type        = string
  default     = "production"
}

variable "project_name" {
  description = "Project identifier"
  type        = string
  default     = "video-ai-platform"
}

variable "db_instance_class" {
  description = "RDS PostgreSQL instance type"
  type        = string
  default     = "db.r6g.large"
}

variable "db_name" {
  description = "Database name"
  type        = string
  default     = "video_ai_db"
}

variable "db_username" {
  description = "Database administrator username"
  type        = string
  default     = "platform_admin"
}
