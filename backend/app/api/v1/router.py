from fastapi import APIRouter
from backend.app.api.v1.endpoints import (
    auth,
    users,
    workspaces,
    tasks,
    cycles,
    research,
    scripts,
    media,
    approvals,
    publishing,
    analytics,
    social_accounts,
    webhooks,
    avatars,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(workspaces.router, prefix="/workspaces", tags=["Workspaces"])
api_router.include_router(tasks.router, prefix="/tasks", tags=["Tasks"])
api_router.include_router(cycles.router, prefix="/cycles", tags=["Cycles"])
api_router.include_router(research.router, prefix="/research", tags=["Research"])
api_router.include_router(scripts.router, prefix="/scripts", tags=["Scripts"])
api_router.include_router(media.router, prefix="/media", tags=["Media"])
api_router.include_router(approvals.router, prefix="/approvals", tags=["Approvals"])
api_router.include_router(publishing.router, prefix="/publishing", tags=["Publishing"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(social_accounts.router, prefix="/social-accounts", tags=["Social Accounts"])
api_router.include_router(webhooks.router, prefix="/webhooks", tags=["Webhooks"])
api_router.include_router(avatars.router, prefix="/avatars", tags=["Avatars"])
