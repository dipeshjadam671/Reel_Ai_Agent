from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.session import get_db
from backend.app.db.repositories.publication_repository import PublicationRepository
from backend.app.schemas.publishing import PublicationOut
from backend.app.api.dependencies import get_current_workspace_id

router = APIRouter()

@router.get("", response_model=List[PublicationOut])
async def list_publications(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    workspace_id: str = Depends(get_current_workspace_id),
    db: AsyncSession = Depends(get_db)
):
    repo = PublicationRepository(db)
    pubs = await repo.list_by_workspace(workspace_id, skip=skip, limit=limit)
    out = []
    for p in pubs:
        views = sum(m.views for m in p.metrics) if p.metrics else 0
        likes = sum(m.likes for m in p.metrics) if p.metrics else 0
        shares = sum(m.shares for m in p.metrics) if p.metrics else 0
        out.append(PublicationOut(
            id=p.id,
            cycle_id=p.cycle_id,
            platform=p.platform,
            status=p.status,
            platform_post_id=p.platform_post_id,
            permalink=p.permalink,
            published_at=p.published_at,
            error_message=p.error_message,
            views=views,
            likes=likes,
            shares=shares
        ))
    return out
