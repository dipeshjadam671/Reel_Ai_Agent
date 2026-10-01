import uuid
import asyncio
from collections import defaultdict
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.constants import CycleStatus
from backend.app.core.exceptions import NotFoundError, AppException
from backend.app.core.constants import ErrorCode
from backend.app.core.logging import logger
from backend.app.db.models.cycle import Cycle
from backend.app.db.models.approval import Approval
from backend.app.db.repositories.cycle_repository import CycleRepository
from backend.app.db.repositories.task_repository import TaskRepository
from backend.app.workflows.content_cycle import ContentCycleWorkflow
from backend.app.services.audit_service import AuditService

_task_locks: Dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)

class CycleService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.cycle_repo = CycleRepository(session)
        self.task_repo = TaskRepository(session)
        self.workflow = ContentCycleWorkflow(session)
        self.audit = AuditService(session)

    async def get_cycle(self, workspace_id: str, cycle_id: str) -> Cycle:
        cycle = await self.cycle_repo.get_by_id(workspace_id, cycle_id)
        if not cycle:
            raise NotFoundError(f"Cycle {cycle_id} not found in workspace")
        return cycle

    async def list_cycles(self, workspace_id: str, task_id: Optional[str] = None, skip: int = 0, limit: int = 50) -> List[Cycle]:
        if task_id:
            return await self.cycle_repo.list_by_task(workspace_id, task_id, skip=skip, limit=limit)
        return await self.cycle_repo.list_by_workspace(workspace_id, skip=skip, limit=limit)

    async def trigger_cycle(
        self,
        workspace_id: str,
        task_id: str,
        user_id: Optional[str] = None,
        override_topic: Optional[str] = None,
        force: bool = False
    ) -> Cycle:
        task = await self.task_repo.get_by_id(workspace_id, task_id)
        if not task:
            raise NotFoundError(f"Task {task_id} not found")

        lock = _task_locks[task_id]
        async with lock:
            # Check existing cycles for this task to guarantee strictly 1 video per task
            existing_cycles = await self.cycle_repo.list_by_task(workspace_id, task_id, limit=10)

            # 1. If an active in-progress cycle exists, do not duplicate! Return it immediately.
            in_progress = [
                c for c in existing_cycles
                if c.status in (
                    CycleStatus.CREATED.value,
                    CycleStatus.RESEARCHING.value,
                    CycleStatus.PRODUCING.value,
                    "scripting",
                    "rendering",
                    "qa"
                )
            ]
            if in_progress:
                logger.info(
                    f"Task {task_id} already has an active in-progress cycle {in_progress[0].id}. "
                    f"Returning existing cycle to prevent duplicate runs."
                )
                return await self.get_cycle(workspace_id, in_progress[0].id)

            # 2. If a cycle is already pending approval or published/completed, enforce single video rule
            if not force:
                ready_cycles = [
                    c for c in existing_cycles
                    if c.status in (CycleStatus.PENDING_APPROVAL.value, CycleStatus.PUBLISHED.value, "completed")
                ]
                if ready_cycles:
                    logger.info(
                        f"Task {task_id} already has a generated video in cycle {ready_cycles[0].id} "
                        f"(status: {ready_cycles[0].status}). Returning existing cycle (1 video per task policy)."
                    )
                    return await self.get_cycle(workspace_id, ready_cycles[0].id)

            # 3. Create fresh cycle and execute
            thread_id = f"thread_{uuid.uuid4().hex[:16]}"
            cycle = Cycle(
                workspace_id=workspace_id,
                task_id=task_id,
                thread_id=thread_id,
                status=CycleStatus.CREATED.value,
            )
            cycle = await self.cycle_repo.create(cycle)

            await self.audit.log_event(
                workspace_id=workspace_id,
                user_id=user_id,
                action="CYCLE_TRIGGERED",
                entity_type="cycle",
                entity_id=cycle.id,
                details={"task_id": task_id, "topic": task.topic}
            )

            # Run cycle through workflow
            await self.workflow.execute_cycle(workspace_id, cycle.id)
            return await self.get_cycle(workspace_id, cycle.id)

    async def approve_cycle(self, workspace_id: str, cycle_id: str, user_id: Optional[str] = None) -> Cycle:
        cycle = await self.get_cycle(workspace_id, cycle_id)
        approval = Approval(
            workspace_id=workspace_id,
            cycle_id=cycle_id,
            user_id=user_id,
            action="approved"
        )
        self.session.add(approval)

        await self.workflow.resume_with_approval(workspace_id, cycle_id, action="approved")
        await self.audit.log_event(
            workspace_id=workspace_id,
            user_id=user_id,
            action="CYCLE_APPROVED",
            entity_type="cycle",
            entity_id=cycle_id,
            details={"action": "approved"}
        )
        return await self.get_cycle(workspace_id, cycle_id)

    async def reject_cycle(self, workspace_id: str, cycle_id: str, user_id: Optional[str] = None, feedback: Optional[str] = None) -> Cycle:
        cycle = await self.get_cycle(workspace_id, cycle_id)
        approval = Approval(
            workspace_id=workspace_id,
            cycle_id=cycle_id,
            user_id=user_id,
            action="rejected",
            feedback=feedback
        )
        self.session.add(approval)
        cycle.status = CycleStatus.REJECTED.value
        await self.cycle_repo.update(cycle)

        await self.audit.log_event(
            workspace_id=workspace_id,
            user_id=user_id,
            action="CYCLE_REJECTED",
            entity_type="cycle",
            entity_id=cycle_id,
            details={"action": "rejected", "feedback": feedback}
        )
        return await self.get_cycle(workspace_id, cycle_id)

    async def regenerate_cycle(self, workspace_id: str, cycle_id: str, user_id: Optional[str] = None, feedback: Optional[str] = None) -> Cycle:
        cycle = await self.get_cycle(workspace_id, cycle_id)
        approval = Approval(
            workspace_id=workspace_id,
            cycle_id=cycle_id,
            user_id=user_id,
            action="regenerate",
            feedback=feedback
        )
        self.session.add(approval)

        await self.workflow.resume_with_approval(workspace_id, cycle_id, action="regenerate", feedback=feedback)
        await self.audit.log_event(
            workspace_id=workspace_id,
            user_id=user_id,
            action="CYCLE_REGENERATION_REQUESTED",
            entity_type="cycle",
            entity_id=cycle_id,
            details={"action": "regenerate", "feedback": feedback}
        )
        return await self.get_cycle(workspace_id, cycle_id)
