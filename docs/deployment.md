# Deployment Guide

## 1. Local Development (Docker Compose)

Run the full stack with single command:
```bash
docker compose up -d
```
Services started:
- `video_ai_postgres`: PostgreSQL 16 with pgvector on port 5432
- `video_ai_redis`: Redis 7 on port 6379
- `video_ai_minio`: S3-compatible MinIO object storage on port 9000/9001
- `video_ai_backend`: FastAPI application on port 8000
- `video_ai_worker`: Async video rendering & cycle worker
- `video_ai_frontend`: Next.js 14 dashboard on port 3000

## 2. Production Deployment

### Kubernetes
Manifests are in `infrastructure/kubernetes/`:
- `namespace.yaml`: Production namespace isolation.
- `backend.yaml`: Horizontal auto-scaling FastAPI pods.
- `workers.yaml`: Compute pods with FFmpeg binary support.
- `redis.yaml`: Clustered Redis cache.
- `ingress.yaml`: TLS termination, routing `/api` to backend and `/` to frontend.

### AWS Infrastructure (Terraform)
Located in `infrastructure/terraform/`:
- RDS Aurora PostgreSQL with pgvector extension enabled.
- ElastiCache Redis cluster.
- S3 Bucket for permanent render and asset storage with CloudFront CDN distribution.
- IAM roles with fine-grained access policies.
