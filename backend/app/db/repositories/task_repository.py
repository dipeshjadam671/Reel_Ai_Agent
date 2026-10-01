from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.models.task import Task

class TaskRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, workspace_id: str, task_id: str) -> Optional[Task]:
        base_stmt = select(Task).options(selectinload(Task.cycles))
        if workspace_id:
            stmt = base_stmt.where(Task.workspace_id == workspace_id, Task.id == task_id)
            result = await self.session.execute(stmt)
            task = result.scalars().first()
            if task:
                return task

        stmt = base_stmt.where(Task.id == task_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_by_workspace(self, workspace_id: str, skip: int = 0, limit: int = 50) -> List[Task]:
        stmt = (
            select(Task)
            .where(Task.workspace_id == workspace_id)
            .options(selectinload(Task.cycles))
            .order_by(Task.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def create(self, task: Task) -> Task:
        self.session.add(task)
        await self.session.flush()
        return task

    async def update(self, task: Task) -> Task:
        await self.session.flush()
        return task

    async def delete(self, workspace_id: str, task_id: str) -> bool:
        task = await self.get_by_id(workspace_id, task_id)
        if task:
            await self.session.delete(task)
            await self.session.flush()
            return True
        return False
