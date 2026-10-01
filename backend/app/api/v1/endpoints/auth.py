from datetime import timedelta
import re
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.security import get_password_hash, verify_password, create_access_token
from backend.app.core.constants import UserRole
from backend.app.db.session import get_db
from backend.app.db.models.user import User, WorkspaceMember
from backend.app.db.models.workspace import Workspace
from backend.app.schemas.auth import UserCreate, UserLogin, UserOut, Token
from backend.app.api.dependencies import get_current_user

router = APIRouter()

@router.post("/register", response_model=Token)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == user_in.email)
    existing = (await db.execute(stmt)).scalars().first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
    )
    db.add(user)
    await db.flush()

    # Automatically create personal workspace for user
    clean_name = user_in.full_name or user_in.email.split("@")[0]
    slug = re.sub(r'[^a-zA-Z0-9]', '-', clean_name.lower()) + f"-{user.id[:6]}"
    ws = Workspace(name=f"{clean_name}'s Workspace", slug=slug)
    db.add(ws)
    await db.flush()

    member = WorkspaceMember(
        user_id=user.id,
        workspace_id=ws.id,
        role=UserRole.OWNER.value
    )
    db.add(member)
    await db.commit()

    token = create_access_token(subject=user.id, workspace_id=ws.id, role=UserRole.OWNER.value)
    return Token(access_token=token, workspace_id=ws.id, role=UserRole.OWNER.value)

@router.post("/login", response_model=Token)
async def login(
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    content_type = request.headers.get("content-type", "")
    email = None
    password = None

    body_bytes = await request.body()
    body_str = body_bytes.decode("utf-8", errors="ignore")

    if "application/json" in content_type:
        try:
            import json
            data = json.loads(body_str) if body_str else {}
            email = data.get("email") or data.get("username")
            password = data.get("password")
        except Exception:
            pass
    else:
        try:
            from urllib.parse import parse_qs
            parsed = parse_qs(body_str)
            email_vals = parsed.get("email") or parsed.get("username")
            pass_vals = parsed.get("password")
            if email_vals:
                email = email_vals[0]
            if pass_vals:
                password = pass_vals[0]
        except Exception:
            pass

    if not email or not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email and password are required"
        )

    stmt = select(User).where(User.email == str(email).strip())
    user = (await db.execute(stmt)).scalars().first()
    if not user or not verify_password(str(password), user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # Get primary workspace
    mem_stmt = select(WorkspaceMember).where(WorkspaceMember.user_id == user.id)
    member = (await db.execute(mem_stmt)).scalars().first()
    ws_id = member.workspace_id if member else None
    role = member.role if member else UserRole.EDITOR.value

    token = create_access_token(subject=user.id, workspace_id=ws_id, role=role)
    return Token(access_token=token, workspace_id=ws_id, role=role)

@router.get("/me", response_model=UserOut)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user
