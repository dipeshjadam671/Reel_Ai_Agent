from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.session import get_db
from backend.app.db.models.workspace import Workspace
from backend.app.db.models.cycle import Cycle
from backend.app.db.models.publication import Publication
from backend.app.db.models.metric import Metric
from backend.app.db.models.spend import SpendLedger
from backend.app.schemas.analytics import WorkspaceAnalyticsOut, SpendLedgerOut
from backend.app.api.dependencies import get_current_workspace_id

router = APIRouter()

@router.get("", response_model=WorkspaceAnalyticsOut)
async def get_analytics(
    workspace_id: str = Depends(get_current_workspace_id),
    db: AsyncSession = Depends(get_db)
):
    ws_res = await db.execute(select(Workspace).where(Workspace.id == workspace_id))
    ws = ws_res.scalars().first()
    monthly_budget = ws.monthly_budget_usd if ws else 50.0

    # Total cycles
    cycles_res = await db.execute(select(func.count(Cycle.id)).where(Cycle.workspace_id == workspace_id))
    total_cycles = cycles_res.scalar() or 0

    # Total published
    pubs_res = await db.execute(select(func.count(Publication.id)).where(Publication.workspace_id == workspace_id, Publication.status == "published"))
    total_pubs = pubs_res.scalar() or 0

    # Total metrics
    metrics_res = await db.execute(
        select(
            func.sum(Metric.views),
            func.sum(Metric.likes),
            func.sum(Metric.shares)
        ).where(Metric.workspace_id == workspace_id)
    )
    v, l, s = metrics_res.first() or (0, 0, 0)

    # Spend
    spend_res = await db.execute(select(func.sum(SpendLedger.amount)).where(SpendLedger.workspace_id == workspace_id))
    total_spend = spend_res.scalar() or 0.0

    # Recent spend
    recent_spend_res = await db.execute(
        select(SpendLedger).where(SpendLedger.workspace_id == workspace_id).order_by(SpendLedger.created_at.desc()).limit(10)
    )
    recent_spend = list(recent_spend_res.scalars().all())

    return WorkspaceAnalyticsOut(
        total_videos_created=total_cycles,
        total_videos_published=total_pubs,
        total_views=int(v or 0),
        total_likes=int(l or 0),
        total_shares=int(s or 0),
        total_spend_usd=round(float(total_spend), 2),
        monthly_budget_usd=monthly_budget,
        recent_spend_records=recent_spend
    )
