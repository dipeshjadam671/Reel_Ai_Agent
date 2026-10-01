from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.models.publication import Publication

class PublicationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_by_workspace(self, workspace_id: str, skip: int = 0, limit: int = 50) -> List[Publication]:
        stmt = (
            select(Publication)
            .where(Publication.workspace_id == workspace_id)
            .options(selectinload(Publication.metrics))
            .order_by(Publication.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_by_id(self, workspace_id: str, publication_id: str) -> Optional[Publication]:
        stmt = (
            select(Publication)
            .where(Publication.workspace_id == workspace_id, Publication.id == publication_id)
            .options(selectinload(Publication.metrics))
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def create(self, publication: Publication) -> Publication:
        self.session.add(publication)
        await self.session.flush()
        return publication

    async def update(self, publication: Publication) -> Publication:
        await self.session.flush()
        return publication
