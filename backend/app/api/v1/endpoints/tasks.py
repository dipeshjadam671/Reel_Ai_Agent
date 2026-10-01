from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.session import get_db
from backend.app.schemas.task import TaskCreate, TaskUpdate, TaskOut
from backend.app.schemas.cycle import CycleOut, CycleRunRequest
from backend.app.services.task_service import TaskService
from backend.app.services.cycle_service import CycleService
from backend.app.api.dependencies import get_current_user, get_current_workspace_id
from backend.app.db.models.user import User

router = APIRouter()

@router.get("", response_model=List[TaskOut])
async def list_tasks(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    workspace_id: str = Depends(get_current_workspace_id),
    db: AsyncSession = Depends(get_db)
):
    service = TaskService(db)
    return await service.list_tasks(workspace_id, skip=skip, limit=limit)

@router.post("", response_model=TaskOut)
async def create_task(
    task_in: TaskCreate,
    workspace_id: str = Depends(get_current_workspace_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = TaskService(db)
    return await service.create_task(workspace_id, task_in, user_id=current_user.id)

@router.get("/{task_id}", response_model=TaskOut)
async def get_task(
    task_id: str,
    workspace_id: str = Depends(get_current_workspace_id),
    db: AsyncSession = Depends(get_db)
):
    service = TaskService(db)
    return await service.get_task(workspace_id, task_id)

@router.patch("/{task_id}", response_model=TaskOut)
async def update_task(
    task_id: str,
    task_in: TaskUpdate,
    workspace_id: str = Depends(get_current_workspace_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = TaskService(db)
    return await service.update_task(workspace_id, task_id, task_in, user_id=current_user.id)

@router.post("/{task_id}/run", response_model=CycleOut)
async def run_task(
    task_id: str,
    run_req: Optional[CycleRunRequest] = None,
    workspace_id: str = Depends(get_current_workspace_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    cycle_service = CycleService(db)
    override = run_req.override_topic if run_req else None
    cycle = await cycle_service.trigger_cycle(
        workspace_id=workspace_id,
        task_id=task_id,
        user_id=current_user.id,
        override_topic=override
    )
    return cycle

@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: str,
    workspace_id: str = Depends(get_current_workspace_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = TaskService(db)
    await service.delete_task(workspace_id, task_id, user_id=current_user.id)
    return None

