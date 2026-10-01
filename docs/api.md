# API Specification (v1)

Base URL: `/api/v1`

## Authentication & Workspaces
- `POST /auth/register`: Create a new user account.
- `POST /auth/login`: Authenticate and obtain JWT access token.
- `GET /auth/me`: Get current user info.
- `GET /workspaces`: List workspaces accessible to user.
- `POST /workspaces`: Create a new tenant workspace.

## Tasks & Cycles
- `GET /tasks`: List content tasks for active workspace.
- `POST /tasks`: Create content task (topic, seed script, language, avatar config, schedule, platform targets).
- `GET /tasks/{task_id}`: Retrieve task details.
- `PATCH /tasks/{task_id}`: Update task configuration.
- `POST /tasks/{task_id}/run`: Immediately trigger a new generation cycle.

## Cycles & Review
- `GET /cycles/{cycle_id}`: Get complete cycle details and current agent status.
- `GET /cycles/{cycle_id}/status`: Lightweight status polling endpoint.
- `GET /cycles/{cycle_id}/preview`: Video render preview URL, script, and metadata.
- `GET /cycles/{cycle_id}/sources`: Research sources and claims.
- `GET /cycles/{cycle_id}/script`: Structured script breakdown.
- `GET /cycles/{cycle_id}/assets`: Curated media assets with licensing.

## Approval Gate
- `POST /cycles/{cycle_id}/approve`: Approve cycle and proceed to publishing.
- `POST /cycles/{cycle_id}/reject`: Reject video.
- `POST /cycles/{cycle_id}/regenerate`: Request regeneration with specific feedback.

## Social Accounts & Publishing
- `GET /social-accounts`: List connected social channels.
- `POST /social-accounts/connect`: Initiate OAuth connection for YouTube, Instagram, or TikTok.
- `GET /publications`: List published videos across channels.

## Analytics & Webhooks
- `GET /analytics`: Workspace-level performance metrics and spend ledger.
- `POST /webhooks/{provider}`: Asynchronous callback endpoint for external providers (HeyGen, ElevenLabs, etc.).
