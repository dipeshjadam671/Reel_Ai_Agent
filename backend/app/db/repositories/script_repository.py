from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.models.script import Script

class ScriptRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_cycle(self, workspace_id: str, cycle_id: str) -> Optional[Script]:
        stmt = select(Script).where(Script.workspace_id == workspace_id, Script.cycle_id == cycle_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def create(self, script: Script) -> Script:
        self.session.add(script)
        await self.session.flush()
        return script

    async def update(self, script: Script) -> Script:
        await self.session.flush()
        return script
