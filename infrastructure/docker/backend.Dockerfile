FROM python:3.12-slim AS base

# Install system dependencies (FFmpeg, libpq for PostgreSQL, gcc for native extensions)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libpq-dev \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

# Install python dependencies
COPY pyproject.toml .
RUN pip install --no-cache-dir -e .

# Copy application source
COPY backend/ ./backend/
COPY alembic.ini .

# Set environment
ENV PYTHONPATH=/workspace \
    PORT=8000 \
    PYTHONUNBUFFERED=1

EXPOSE 8000

# Healthcheck
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start FastAPI application
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
