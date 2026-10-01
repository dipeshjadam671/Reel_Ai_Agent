from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.session import get_db
from backend.app.db.models.asset import Asset
from backend.app.schemas.media import AssetOut
from backend.app.api.dependencies import get_current_workspace_id

router = APIRouter()

@router.get("/assets", response_model=List[AssetOut])
async def list_workspace_assets(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    workspace_id: str = Depends(get_current_workspace_id),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Asset).where(Asset.workspace_id == workspace_id).order_by(Asset.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(stmt)
    return list(result.scalars().all())
