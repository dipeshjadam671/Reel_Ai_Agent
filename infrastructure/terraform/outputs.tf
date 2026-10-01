output "s3_bucket_name" {
  description = "S3 bucket for video assets and renders"
  value       = aws_s3_bucket.assets.id
}

output "rds_endpoint" {
  description = "PostgreSQL endpoint"
  value       = aws_db_instance.postgres.endpoint
}

output "redis_endpoint" {
  description = "ElastiCache Redis endpoint"
  value       = aws_elasticache_cluster.redis.cache_nodes[0].address
}

output "ecr_backend_url" {
  description = "ECR Backend repository URL"
  value       = aws_ecr_repository.backend.repository_url
}

output "ecr_frontend_url" {
  description = "ECR Frontend repository URL"
  value       = aws_ecr_repository.frontend.repository_url
}

output "ecr_worker_url" {
  description = "ECR Worker repository URL"
  value       = aws_ecr_repository.worker.repository_url
}
