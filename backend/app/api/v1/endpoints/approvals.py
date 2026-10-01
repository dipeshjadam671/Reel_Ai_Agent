from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.session import get_db
from backend.app.db.models.approval import Approval
from backend.app.db.models.cycle import Cycle
from backend.app.core.constants import CycleStatus
from backend.app.schemas.approval import ApprovalOut
from backend.app.schemas.cycle import CycleOut
from backend.app.api.dependencies import get_current_workspace_id

router = APIRouter()

@router.get("", response_model=List[ApprovalOut])
async def list_approvals(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    workspace_id: str = Depends(get_current_workspace_id),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Approval).where(Approval.workspace_id == workspace_id).order_by(Approval.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())

@router.get("/pending", response_model=List[CycleOut])
async def list_pending_approvals(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    workspace_id: str = Depends(get_current_workspace_id),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Cycle)
        .where(
            Cycle.workspace_id == workspace_id,
            Cycle.status == CycleStatus.PENDING_APPROVAL.value
        )
        .order_by(Cycle.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())

