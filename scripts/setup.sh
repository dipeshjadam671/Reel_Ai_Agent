#!/usr/bin/env bash
set -e

echo "=== Setting up Autonomous AI Video Generation Platform ==="

# 1. Environment file setup
if [ ! -f .env ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
fi

# 2. Virtual environment setup
if [ ! -d .venv ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv .venv
fi

echo "Installing backend dependencies..."
.venv/bin/pip install --upgrade pip
.venv/bin/pip install -e ".[dev]"

# 3. Docker Services setup
echo "Starting PostgreSQL and Redis containers..."
docker compose up -d postgres redis

echo "Waiting for PostgreSQL to be ready..."
until docker exec video_ai_postgres pg_isready -U postgres -d video_ai_db; do
  sleep 1
done

# 4. Database Migrations
echo "Applying database migrations..."
PYTHONPATH=. .venv/bin/alembic upgrade head

# 5. Database Seeding
echo "Seeding platform initial users, workspace, and demo tasks..."
PYTHONPATH=. .venv/bin/python scripts/seed_db.py

# 6. Frontend Setup
echo "Installing frontend dependencies..."
cd frontend
npm install
cd ..

echo "=== Setup complete! Run ./scripts/dev.sh to launch the platform ==="
