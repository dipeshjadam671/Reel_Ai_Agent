import re
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.constants import UserRole
from backend.app.db.session import get_db
from backend.app.db.models.user import User, WorkspaceMember
from backend.app.db.models.workspace import Workspace
from backend.app.schemas.auth import WorkspaceCreate, WorkspaceOut
from backend.app.api.dependencies import get_current_user

router = APIRouter()

@router.get("", response_model=List[WorkspaceOut])
async def list_workspaces(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Workspace)
        .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
        .where(WorkspaceMember.user_id == current_user.id)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())

@router.post("", response_model=WorkspaceOut)
async def create_workspace(
    ws_in: WorkspaceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    slug_base = re.sub(r'[^a-zA-Z0-9]', '-', ws_in.name.lower()).strip("-")
    slug = f"{slug_base}-{current_user.id[:6]}"

    ws = Workspace(
        name=ws_in.name,
        slug=slug,
        monthly_budget_usd=ws_in.monthly_budget_usd or 50.0
    )
    db.add(ws)
    await db.flush()

    member = WorkspaceMember(
        user_id=current_user.id,
        workspace_id=ws.id,
        role=UserRole.OWNER.value
    )
    db.add(member)
    await db.commit()
    return ws
