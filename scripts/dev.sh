#!/usr/bin/env bash
set -e

echo "=== Launching Autonomous AI Video Studio Development Services ==="

# Ensure Docker containers are running
docker compose up -d postgres redis

# Trap SIGINT to kill background jobs cleanly
cleanup() {
    echo ""
    echo "Stopping platform services..."
    kill $(jobs -p) 2>/dev/null || true
    exit 0
}
trap cleanup SIGINT SIGTERM

echo "Starting Celery Worker..."
PYTHONPATH=. .venv/bin/celery -A backend.app.workers.tasks.celery_app worker --loglevel=info -c 2 &

echo "Starting FastAPI Backend API on http://localhost:8000..."
PYTHONPATH=. .venv/bin/uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload &

echo "Starting Next.js Frontend Studio on http://localhost:3000..."
cd frontend && npm run dev &

wait
