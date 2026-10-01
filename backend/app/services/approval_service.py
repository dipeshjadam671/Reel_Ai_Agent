from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.models.approval import Approval

class ApprovalService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list_approvals_for_cycle(self, workspace_id: str, cycle_id: str) -> List[Approval]:
        stmt = (
            select(Approval)
            .where(Approval.workspace_id == workspace_id, Approval.cycle_id == cycle_id)
            .order_by(Approval.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
