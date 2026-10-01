from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.models.cycle import Cycle

class CycleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, workspace_id: str, cycle_id: str) -> Optional[Cycle]:
        base_stmt = (
            select(Cycle)
            .options(
                selectinload(Cycle.task),
                selectinload(Cycle.sources),
                selectinload(Cycle.script),
                selectinload(Cycle.assets),
                selectinload(Cycle.render),
                selectinload(Cycle.approvals),
                selectinload(Cycle.publications),
            )
        )
        if workspace_id:
            stmt = base_stmt.where(Cycle.workspace_id == workspace_id, Cycle.id == cycle_id)
            result = await self.session.execute(stmt)
            cycle = result.scalars().first()
            if cycle:
                return cycle

        stmt = base_stmt.where(Cycle.id == cycle_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_by_task(self, workspace_id: str, task_id: str, skip: int = 0, limit: int = 50) -> List[Cycle]:
        stmt = (
            select(Cycle)
            .where(Cycle.workspace_id == workspace_id, Cycle.task_id == task_id)
            .order_by(Cycle.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_by_workspace(self, workspace_id: str, skip: int = 0, limit: int = 50) -> List[Cycle]:
        stmt = (
            select(Cycle)
            .where(Cycle.workspace_id == workspace_id)
            .order_by(Cycle.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, cycle: Cycle) -> Cycle:
        self.session.add(cycle)
        await self.session.flush()
        return cycle

    async def update(self, cycle: Cycle) -> Cycle:
        await self.session.flush()
        return cycle
