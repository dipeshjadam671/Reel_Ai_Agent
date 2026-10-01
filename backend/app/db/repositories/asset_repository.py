from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.models.asset import Asset

class AssetRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_by_cycle(self, workspace_id: str, cycle_id: str) -> List[Asset]:
        stmt = select(Asset).where(Asset.workspace_id == workspace_id, Asset.cycle_id == cycle_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, asset: Asset) -> Asset:
        self.session.add(asset)
        await self.session.flush()
        return asset

    async def bulk_create(self, assets: List[Asset]) -> List[Asset]:
        self.session.add_all(assets)
        await self.session.flush()
        return assets
