from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.session import get_db
from backend.app.db.models.source import Source
from backend.app.schemas.research import SourceItem
from backend.app.api.dependencies import get_current_workspace_id

router = APIRouter()

@router.get("/sources", response_model=List[SourceItem])
async def list_workspace_sources(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    workspace_id: str = Depends(get_current_workspace_id),
    db: AsyncSession = Depends(get_db)
):
    stmt = select(Source).where(Source.workspace_id == workspace_id).offset(skip).limit(limit)
    result = await db.execute(stmt)
    sources = result.scalars().all()
    return [
        SourceItem(
            title=s.title,
            url=s.url,
            domain=s.domain,
            summary=s.summary,
            credibility_score=s.credibility_score
        )
        for s in sources
    ]
