FROM python:3.12-slim AS base

RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

COPY backend/ ./backend/
COPY alembic.ini .

ENV PYTHONPATH=/workspace \
    PYTHONUNBUFFERED=1

# Start Celery worker for async agent cycle & rendering tasks
CMD ["celery", "-A", "backend.app.workers.tasks.celery_app", "worker", "--loglevel=info", "-c", "4"]
