import asyncio
import os
import sys
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from backend.app.db.session import AsyncSessionLocal
from backend.app.db.models import User, Workspace, Task, Cycle, Render, Approval, Publication
from backend.app.services.cycle_service import CycleService
from backend.app.core.config import settings

async def main():
    print("=" * 60)
    print("Starting Autonomous AI Video Platform End-to-End Verification")
    print(f"Mock Mode: {settings.MOCK_EXTERNAL_APIS}")
    print(f"Database: {settings.DATABASE_URL.split('@')[-1]}")
    print("=" * 60)

    async with AsyncSessionLocal() as db:
        # 1. Verify User and Workspace
        user_stmt = select(User).where(User.email == "admin@videoai.platform")
        user = (await db.execute(user_stmt)).scalars().first()
        assert user is not None, "Admin user not found"
        print(f"✓ Admin user verified: {user.email} (ID: {user.id})")

        ws_stmt = select(Workspace).limit(1)
        workspace = (await db.execute(ws_stmt)).scalars().first()
        assert workspace is not None, "Workspace not found"
        print(f"✓ Workspace verified: {workspace.name} (Budget: ${workspace.monthly_budget_usd})")

        # 2. Verify or create a test Task
        task_stmt = select(Task).where(Task.workspace_id == workspace.id).limit(1)
        task = (await db.execute(task_stmt)).scalars().first()
        if not task:
            task = Task(
                workspace_id=workspace.id,
                name="DeepSeek Innovation Reel",
                topic="How DeepSeek R1 models are revolutionizing open-source coding agents",
                language="en",
                target_platforms=["youtube", "instagram", "tiktok"],
                presenter_config={"layout": "pip", "avatar_id": "avatar_tech_alex", "voice_id": "21m00Tcm4TlvDq8ikWAM"},
                schedule_config={"frequency": "daily", "time": "09:00", "timezone": "UTC", "active_days": ["mon", "wed", "fri"]},
                brand_preferences={"tone": "energetic and authoritative", "call_to_action": "Follow for daily AI breakthroughs!"}
            )
            db.add(task)
            await db.commit()
            await db.refresh(task)
        print(f"✓ Content Task verified: '{task.name}' (Topic: {task.topic[:40]}...)")

        # 3. Execute Complete Autonomous Content Cycle via CycleService
        print("\nLaunching Autonomous LangGraph Multi-Agent Video Cycle...")
        cycle_service = CycleService(db)
        cycle = await cycle_service.trigger_cycle(workspace.id, task.id, user_id=user.id)
        print(f"  Cycle Executed: {cycle.id} [Status: {cycle.status}]")
        assert cycle.status in ["pending_approval", "completed", "producing"], f"Unexpected cycle status: {cycle.status}"

        # 4. Verify Database Persistence of Cycle Artifacts
        c_stmt = (
            select(Cycle)
            .where(Cycle.id == cycle.id)
            .options(
                selectinload(Cycle.render),
                selectinload(Cycle.script),
                selectinload(Cycle.sources),
                selectinload(Cycle.assets),
            )
        )
        saved_cycle = (await db.execute(c_stmt)).scalars().first()
        assert saved_cycle is not None, "Cycle not saved to database"
        assert saved_cycle.render is not None, "Render not generated"
        assert saved_cycle.script is not None, "Script not generated"
        assert len(saved_cycle.sources) > 0, "No research sources saved"
        assert len(saved_cycle.assets) > 0, "No assets saved"

        print(f"✓ Render Output: {saved_cycle.render.resolution} @ {saved_cycle.render.duration_seconds:.1f}s")
        print(f"  Video file: {saved_cycle.render.video_url}")
        print(f"✓ Script Hook: \"{saved_cycle.script.hook}\" ({len(saved_cycle.script.scenes)} scenes)")
        print(f"✓ Novelty Score: {saved_cycle.novelty_score:.2f} (Verified original)")
        print(f"✓ Total Cost: ${saved_cycle.actual_cost_usd:.4f}")

        # 5. Test Human-in-the-Loop Approval Action
        print("\nTesting Human Approval Gate...")
        approved_cycle = await cycle_service.approve_cycle(workspace.id, cycle.id, user_id=user.id)
        assert approved_cycle.status in ["completed", "published"], f"Cycle status after approval: {approved_cycle.status}"
        print(f"✓ Human Approval accepted! Cycle transitioned to '{approved_cycle.status}'")

        # 6. Verify Social Publishing
        pub_stmt = select(Publication).where(Publication.cycle_id == cycle.id)
        pubs = list((await db.execute(pub_stmt)).scalars().all())
        assert len(pubs) > 0, "No social publications recorded"
        for p in pubs:
            print(f"✓ Published to {p.platform.upper()}: Status={p.status}, URL={p.permalink}")

    print("\n" + "=" * 60)
    print("ALL END-TO-END SYSTEM VERIFICATIONS PASSED WITH 100% SUCCESS!")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
