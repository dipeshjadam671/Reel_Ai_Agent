# Database Schema & Isolation

## Database Technology
- **Engine**: PostgreSQL 16+
- **Extensions**:
  - `uuid-ossp` or `pgcrypto` for UUID generation.
  - `vector` (pgvector) for embedding similarity search.
  - `age` (Apache AGE) for GraphRAG graph relationship queries (with relational table fallback).

## Tables Overview

```
┌──────────────┐     ┌──────────────┐
│    users     │◀───▶│  workspaces  │
└──────────────┘     └──────┬───────┘
                            │ 1:N
             ┌──────────────┼──────────────┬──────────────┐
             ▼              ▼              ▼              ▼
       ┌──────────┐   ┌───────────┐  ┌───────────┐  ┌───────────┐
       │  tasks   │   │preferences│  │spend_ledger│  │ audit_log │
       └────┬─────┘   └───────────┘  └───────────┘  └───────────┘
            │ 1:N
            ▼
       ┌──────────┐
       │  cycles  │
       └────┬─────┘
            │
    ┌───────┼───────┬──────────┬──────────┬──────────┐
    ▼       ▼       ▼          ▼          ▼          ▼
┌───────┐┌──────┐┌──────┐ ┌─────────┐┌───────────┐┌───────┐
│sources││script││assets│ │ renders ││ approvals ││pubs   │
└───────┘└──────┘└──────┘ └─────────┘└───────────┘└───┬───┘
                                                      │
                                                      ▼
                                                ┌───────────┐
                                                │post_metric│
                                                └───────────┘
```

## Isolation Principles
- Every tenant entity has `workspace_id` indexed.
- Repository layer queries automatically filter by `workspace_id`.
- Foreign keys use `ON DELETE CASCADE` appropriately.
- pgvector columns use Cosine Distance (`vector_cosine_ops`) indexing.
