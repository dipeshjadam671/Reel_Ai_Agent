# Autonomous AI Video Generation & Publishing Platform

An enterprise-grade, multi-tenant SaaS platform that automates short-form video generation from user-configured topics and workflows. Orchestrated by **LangGraph**, the system utilizes a hierarchical multi-agent supervisor pattern with research, scripting, licensed media curation, TTS, talking-head avatars, FFmpeg composition, compliance checking, QA verification, human-in-the-loop approval, and multi-platform social publishing.

---

## 1. Project Overview

The platform enables users to define content generation tasks (specifying topic, seed scripts, target languages such as English or Hindi, presenter avatars, publishing schedules, and social accounts) and continuously generates high-quality 9:16 vertical short-form videos (YouTube Shorts, Instagram Reels, TikTok) through an autonomous pipeline.

### Core Workflow:
1. **Trend Scout & Researcher**: Searches live web sources, synthesizes claims, and extracts citations.
2. **Novelty Guard**: Compares new concepts against previous scripts using hybrid pgvector and GraphRAG.
3. **Scriptwriter & Localization**: Generates structured hook-driven scripts localized to target languages.
4. **Fact Checker**: Validates assertions against research sources.
5. **Storyboard & Asset Curator**: Selects licensed b-roll video/images and background music.
6. **Voice & Presenter**: Synthesizes synchronized voiceover (TTS) and talking-head avatar clips.
7. **Editor / FFmpeg**: Renders 1080x1920 video with dynamic animated subtitles and audio ducking.
8. **Compliance & QA**: Validates licensing, content safety, platform policies, and quality scoring.
9. **Human Approval Gate**: Pauses execution via LangGraph `interrupt()`, awaiting user approval or feedback.
10. **Publisher & Analytics**: Publishes to social channels and monitors performance metrics.

---

## 2. Architecture

```text
                         USER
                           |
                           v
                    +-------------+
                    |  Next.js UI |
                    +------+------+
                           |
                           v
                    +-------------+
                    |   FastAPI   |
                    +------+------+
                           |
                           v
                 +--------------------+
                 |   LangGraph        |
                 | Cycle Supervisor   |
                 +---------+----------+
                           |
        +------------------+------------------+
        |                  |                  |
        v                  v                  v
   RESEARCH            SCRIPTING            MEDIA
   SUBGRAPH            SUBGRAPH            SUBGRAPH
        |                  |                  |
        +------------------+------------------+
                           |
                           v
                    PRODUCTION SUBGRAPH
                           |
                           v
                    COMPLIANCE + QA
                           |
                           v
                    HUMAN APPROVAL
                       /       \
                  REJECT       APPROVE
                    |             |
                    v             v
                REGENERATE    PUBLISHER
                                  |
                  +---------------+---------------+
                  |               |               |
                  v               v               v
               YouTube        Instagram        TikTok
                                  |
                                  v
                              ANALYTICS
```

---

## 3. Folder Structure

```text
autonomous-ai-video-platform/
├── docs/                      # Architecture, agent & API documentation
├── backend/                   # Python 3.12+ FastAPI backend & LangGraph agents
│   ├── app/
│   │   ├── api/               # API endpoints (v1), routers, dependencies
│   │   ├── core/              # Config, security, logging, exceptions
│   │   ├── db/                # Models, session, repositories
│   │   ├── schemas/           # Pydantic request/response schemas
│   │   ├── agents/            # LangGraph multi-agent subgraphs
│   │   ├── workflows/         # End-to-end content cycle workflows
│   │   ├── services/          # Business logic, billing, scheduling
│   │   ├── integrations/      # Provider adapters (LLM, TTS, Avatar, Publish)
│   │   ├── rag/               # Vector store, hybrid search, GraphRAG
│   │   ├── media/             # Video renderer, FFmpeg composition, subtitles
│   │   └── workers/           # Background tasks and Celery queue
│   ├── migrations/            # Alembic database migrations
│   └── tests/                 # Unit, integration, and e2e test suites
├── frontend/                  # Next.js 14 App Router, TypeScript, Tailwind
├── infrastructure/            # Dockerfiles, Kubernetes, Terraform
└── scripts/                   # Setup, seeding, dev scripts
```

---

## 4. Setup & Quickstart

### Prerequisites
- Python 3.12+
- Node.js 20+
- Docker & Docker Compose
- FFmpeg (automatically provided in Docker or fallback via `imageio-ffmpeg`)

### 1. Clone & Configure Environment
```bash
cp .env.example .env
```

### 2. Mock Mode (Zero-Cost Local Development)
By default, `MOCK_EXTERNAL_APIS=true` is set in `.env`. This allows running the entire workflow locally without spending any money on third-party APIs (OpenAI, ElevenLabs, HeyGen, Pexels, YouTube, etc.).

---

## 5. Docker Setup (Recommended)

Start the entire stack (Postgres + pgvector, Redis, MinIO, FastAPI Backend, Celery Worker, Next.js Frontend):

```bash
docker compose up -d
```

- **Frontend Dashboard**: [http://localhost:3000](http://localhost:3000)
- **FastAPI Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **MinIO Storage Console**: [http://localhost:9001](http://localhost:9001)

---

## 6. Local Development (Without Docker)

### Backend Setup
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Run database migrations & seed demo data:
```bash
python scripts/seed_db.py
```

Run FastAPI Backend:
```bash
uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```

Run Celery Worker:
```bash
celery -A backend.app.workers.tasks.celery_app worker --loglevel=info
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

---

## 7. Running Tests

Execute the comprehensive test suite:
```bash
pytest backend/tests/ -v
```

---

## 8. API Documentation

Interactive Swagger documentation is available at `/docs` and ReDoc at `/redoc`.
Key API endpoints include:
- `POST /api/v1/auth/register` & `POST /api/v1/auth/login`
- `POST /api/v1/tasks` & `POST /api/v1/tasks/{id}/run`
- `GET /api/v1/cycles/{id}` & `GET /api/v1/cycles/{id}/preview`
- `POST /api/v1/cycles/{id}/approve` & `POST /api/v1/cycles/{id}/reject`
- `GET /api/v1/analytics`

---

## 9. Production Deployment

Refer to [docs/deployment.md](docs/deployment.md) for detailed Kubernetes and AWS Terraform provisioning guides.
