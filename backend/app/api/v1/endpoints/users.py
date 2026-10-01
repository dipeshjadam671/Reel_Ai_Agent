from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.session import get_db
from backend.app.db.models.user import User
from backend.app.schemas.auth import UserOut
from backend.app.api.dependencies import get_current_user

router = APIRouter()

@router.get("", response_model=List[UserOut])
async def list_users(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    stmt = select(User).limit(50)
    result = await db.execute(stmt)
    return list(result.scalars().all())
