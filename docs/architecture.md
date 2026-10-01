# Architecture Overview: Autonomous AI Video Generation & Publishing Platform

## 1. System Topology

The platform is designed as an event-driven, multi-tenant system structured into distinct layers:

```
                            [ USER / CLIENT ]
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │   Next.js 14 App     │
                         │ (Dashboard, Review,  │
                         │  Approval & Preview) │
                         └──────────┬───────────┘
                                    │ HTTP / WebSocket
                                    ▼
                         ┌──────────────────────┐
                         │   FastAPI Gateway    │
                         │  (Auth, RBAC, Rest)  │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    Service Layer     │
                         │(Task, Cycle, Billing)│
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ LangGraph Supervisor │
                         │ (Hierarchical Graph) │
                         └──────────┬───────────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            ▼                       ▼                       ▼
   ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
   │ Research Sub-   │     │ Scripting Sub-  │     │ Media & Video   │
   │ graph (Trends,  │     │ graph (Writer,  │     │ Subgraph (Audio,│
   │ Sources, Facts) │     │ Localize, Fact) │     │ Avatar, Render) │
   └─────────────────┘     └─────────────────┘     └─────────────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │  Compliance & QA     │
                         │ (Safety Gate, Score) │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │ Human Approval Gate  │
                         │  (Interrupt/Resume)  │
                         └──────────┬───────────┘
                                    │
                        ┌───────────┴───────────┐
                        ▼                       ▼
                [ REGENERATE ]           [ PUBLISHER ]
                 (Feedback Loop)                │
                                                ▼
                                     ┌─────────────────────┐
                                     │ YouTube / Instagram │
                                     │      / TikTok       │
                                     └─────────────────────┘
```

## 2. Architectural Layers

1. **API Layer (`backend/app/api/`)**:
   - Thin route handlers validating incoming schemas.
   - Enforces JWT session validation, tenant workspace isolation, and RBAC permissions.
2. **Service Layer (`backend/app/services/`)**:
   - Encapsulates business logic, state machines, spend tracking, and scheduling calculations.
3. **Workflow & Agent Orchestration (`backend/app/agents/`)**:
   - Built on **LangGraph**. State transitions, subgraph routing, retry logic, and human approval interrupts.
4. **Integration Adapters (`backend/app/integrations/`)**:
   - Protocol-driven interfaces for LLMs, Search engines, Stock media, TTS, Avatar generators, and Social publishers.
   - Includes full mock implementations (`MOCK_EXTERNAL_APIS=true`) for cost-free testing.
5. **Persistence & RAG (`backend/app/db/` & `backend/app/rag/`)**:
   - PostgreSQL 16+ with `pgvector` for semantic search.
   - BM25 full-text search and Apache AGE / relational GraphRAG for entity relation modeling.
   - S3-compatible object storage (AWS S3, MinIO, or Local filesystem).
