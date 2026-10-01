.PHONY: help setup dev run-backend run-worker run-frontend test lint migrate seed docker-up docker-down clean

PYTHON ?= python3
VENV ?= .venv

help:
	@echo "Available commands:"
	@echo "  make setup         - Create virtualenv and install dependencies"
	@echo "  make dev           - Run local development services"
	@echo "  make run-backend   - Start FastAPI backend server"
	@echo "  make run-worker    - Start background task worker"
	@echo "  make run-frontend  - Start Next.js development server"
	@echo "  make test          - Run backend test suite"
	@echo "  make lint          - Run linters (ruff, black, mypy)"
	@echo "  make migrate       - Apply database migrations with Alembic"
	@echo "  make seed          - Seed database with demo tenant & tasks"
	@echo "  make docker-up     - Start all services via Docker Compose"
	@echo "  make docker-down   - Stop Docker Compose services"
	@echo "  make clean         - Remove caches and build artifacts"

setup:
	$(PYTHON) -m venv $(VENV)
	$(VENV)/bin/pip install --upgrade pip setuptools wheel
	$(VENV)/bin/pip install -e ".[dev]"
	cd frontend && npm install

dev:
	bash scripts/dev.sh

run-backend:
	$(VENV)/bin/uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload

run-worker:
	$(VENV)/bin/celery -A backend.app.workers.tasks.celery_app worker --loglevel=info

run-frontend:
	cd frontend && npm run dev

test:
	PYTHONPATH=backend $(VENV)/bin/pytest backend/tests -v

lint:
	$(VENV)/bin/ruff check backend
	$(VENV)/bin/black --check backend

migrate:
	PYTHONPATH=backend $(VENV)/bin/alembic upgrade head

seed:
	PYTHONPATH=backend $(VENV)/bin/python scripts/seed_db.py

docker-up:
	docker compose up -d

docker-down:
	docker compose down

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .coverage htmlcov dist build *.egg-info
