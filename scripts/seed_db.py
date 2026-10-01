import asyncio
import os
import sys

# Ensure project root is in sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from sqlalchemy import select
from backend.app.db.session import AsyncSessionLocal
from backend.app.core.security import get_password_hash
from backend.app.core.constants import UserRole, TaskStatus, CycleStatus
from backend.app.db.models import (
    User,
    Workspace,
    WorkspaceMember,
    Task,
    Cycle,
    Script,
    Source,
    Asset,
    Render,
    Publication,
    Metric,
    SpendLedger,
)

async def seed():
    print("Seeding database with demo tenant and tasks...")
    async with AsyncSessionLocal() as session:
        # 1. Create or get demo user
        stmt = select(User).where(User.email == "admin@videoai.platform")
        user = (await session.execute(stmt)).scalars().first()
        if not user:
            user = User(
                email="admin@videoai.platform",
                hashed_password=get_password_hash("password123"),
                full_name="Alex Rivera",
                is_active=True,
                is_superuser=True
            )
            session.add(user)
            await session.flush()
            print(f"Created admin user: {user.email}")

        # Also create a demo user for quick login
        demo_stmt = select(User).where(User.email == "demo@videoai.platform")
        demo_user = (await session.execute(demo_stmt)).scalars().first()
        if not demo_user:
            demo_user = User(
                email="demo@videoai.platform",
                hashed_password=get_password_hash("demo12345"),
                full_name="Demo Creator",
                is_active=True
            )
            session.add(demo_user)
            await session.flush()

        # 2. Create or get demo workspace
        ws_stmt = select(Workspace).where(Workspace.slug == "autonomous-video-studio")
        workspace = (await session.execute(ws_stmt)).scalars().first()
        if not workspace:
            workspace = Workspace(
                name="Autonomous Video Studio",
                slug="autonomous-video-studio",
                monthly_budget_usd=100.0,
                current_spend_usd=12.50
            )
            session.add(workspace)
            await session.flush()

            # Add memberships
            m1 = WorkspaceMember(user_id=user.id, workspace_id=workspace.id, role=UserRole.OWNER.value)
            m2 = WorkspaceMember(user_id=demo_user.id, workspace_id=workspace.id, role=UserRole.EDITOR.value)
            session.add_all([m1, m2])
            await session.flush()
            print(f"Created workspace: {workspace.name}")

        # 3. Create demo tasks
        t1_stmt = select(Task).where(Task.workspace_id == workspace.id, Task.topic == "The Rise of Autonomous AI Agents in 2026")
        task1 = (await session.execute(t1_stmt)).scalars().first()
        if not task1:
            task1 = Task(
                workspace_id=workspace.id,
                name="Daily AI Agent Breakthroughs",
                topic="The Rise of Autonomous AI Agents in 2026",
                seed_script="Explore how autonomous agents coordinate multi-step workflows without human micro-management.",
                language="en",
                target_platforms=["youtube", "instagram", "tiktok"],
                presenter_config={"avatar_id": "avatar_alex", "voice_id": "voice_en_neutral", "pose": "portrait"},
                schedule_config={"frequency": "daily", "time": "09:00", "timezone": "UTC", "active_days": ["mon", "tue", "wed", "thu", "fri"]},
                brand_preferences={"tone": "high_energy", "call_to_action": "Follow for daily autonomous AI breakthroughs!"},
                status=TaskStatus.ACTIVE.value
            )

            task2 = Task(
                workspace_id=workspace.id,
                name="दैनिक एआई और रोबोटिक्स (Hindi Tech Series)",
                topic="स्वायत्त एआई और रोबोटिक्स का भविष्य",
                seed_script="जानिए कैसे स्वायत्त एआई दुनिया भर में उद्योगों को तेजी से बदल रहा है।",
                language="hi",
                target_platforms=["youtube", "instagram"],
                presenter_config={"avatar_id": "avatar_priya", "voice_id": "voice_hi_female", "pose": "portrait"},
                schedule_config={"frequency": "weekdays", "time": "18:00", "timezone": "Asia/Kolkata", "active_days": ["mon", "tue", "wed", "thu", "fri"]},
                brand_preferences={"tone": "educational", "call_to_action": "ऐसे और वीडियो के लिए सब्सक्राइब करें!"},
                status=TaskStatus.ACTIVE.value
            )
            session.add_all([task1, task2])
            await session.flush()
            print("Created sample content tasks")

        await session.commit()
    print("Database seeding completed successfully!")

if __name__ == "__main__":
    asyncio.run(seed())
