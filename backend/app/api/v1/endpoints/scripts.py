from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.session import get_db
from backend.app.db.models.script import Script
from backend.app.schemas.script import ScriptOut
from backend.app.api.dependencies import get_current_workspace_id

router = APIRouter()

@router.get("", response_model=List[ScriptOut])
async def list_workspace_scripts(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    workspace_id: str = Depends(get_current_workspace_id),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Script).where(Script.workspace_id == workspace_id).order_by(Script.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())
