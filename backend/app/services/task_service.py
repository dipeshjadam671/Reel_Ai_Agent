from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.models.task import Task
from backend.app.db.repositories.task_repository import TaskRepository
from backend.app.schemas.task import TaskCreate, TaskUpdate
from backend.app.core.exceptions import NotFoundError
from backend.app.services.audit_service import AuditService

class TaskService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repo = TaskRepository(session)
        self.audit = AuditService(session)

    async def get_task(self, workspace_id: str, task_id: str) -> Task:
        task = await self.repo.get_by_id(workspace_id, task_id)
        if not task:
            raise NotFoundError(f"Task {task_id} not found in workspace")
        return task

    async def list_tasks(self, workspace_id: str, skip: int = 0, limit: int = 50) -> List[Task]:
        return await self.repo.list_by_workspace(workspace_id, skip=skip, limit=limit)

    async def create_task(self, workspace_id: str, task_in: TaskCreate, user_id: Optional[str] = None) -> Task:
        task = Task(
            workspace_id=workspace_id,
            name=task_in.name,
            topic=task_in.topic,
            seed_script=task_in.seed_script,
            language=task_in.language,
            target_platforms=task_in.target_platforms,
            presenter_config=task_in.presenter_config.model_dump() if task_in.presenter_config else {},
            schedule_config=task_in.schedule_config.model_dump() if task_in.schedule_config else {},
            brand_preferences=task_in.brand_preferences.model_dump() if task_in.brand_preferences else {},
        )
        task = await self.repo.create(task)
        await self.audit.log_event(
            workspace_id=workspace_id,
            user_id=user_id,
            action="TASK_CREATED",
            entity_type="task",
            entity_id=task.id,
            details={"name": task.name, "topic": task.topic}
        )
        return task

    async def update_task(self, workspace_id: str, task_id: str, task_in: TaskUpdate, user_id: Optional[str] = None) -> Task:
        task = await self.get_task(workspace_id, task_id)
        update_data = task_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(task, key, value)
        task = await self.repo.update(task)
        await self.audit.log_event(
            workspace_id=workspace_id,
            user_id=user_id,
            action="TASK_UPDATED",
            entity_type="task",
            entity_id=task.id,
            details=update_data
        )
        return task

    async def delete_task(self, workspace_id: str, task_id: str, user_id: Optional[str] = None) -> bool:
        await self.get_task(workspace_id, task_id)
        deleted = await self.repo.delete(workspace_id, task_id)
        if deleted:
            await self.audit.log_event(
                workspace_id=workspace_id,
                user_id=user_id,
                action="TASK_DELETED",
                entity_type="task",
                entity_id=task_id,
                details={}
            )
        return deleted
