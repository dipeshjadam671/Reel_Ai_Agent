import pytest
from httpx import ASGITransport, AsyncClient
from backend.app.main import app

@pytest.mark.asyncio
async def test_health():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        res = await ac.get("/health")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "healthy"
        assert data["mock_mode"] is True

@pytest.mark.asyncio
async def test_auth_and_workspaces():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # 1. Register new user
        import uuid
        test_email = f"user_{uuid.uuid4().hex[:6]}@example.com"
        reg_res = await ac.post("/api/v1/auth/register", json={
            "email": test_email,
            "password": "Password123!",
            "full_name": "Integration Tester"
        })
        assert reg_res.status_code == 200
        token_data = reg_res.json()
        token = token_data["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 2. Get profile
        me_res = await ac.get("/api/v1/auth/me", headers=headers)
        assert me_res.status_code == 200
        assert me_res.json()["email"] == test_email

        # 3. List workspaces
        ws_res = await ac.get("/api/v1/workspaces", headers=headers)
        assert ws_res.status_code == 200
        workspaces = ws_res.json()
        assert len(workspaces) > 0
        workspace_id = workspaces[0]["id"]
        headers["X-Workspace-Id"] = workspace_id

        # 4. Create content task
        task_res = await ac.post("/api/v1/tasks", json={
            "name": "Integration Video Task",
            "topic": "Autonomous AI Multi-Agent Architecture",
            "seed_script": "Explaining how multi-agent graphs coordinate in production.",
            "language": "en",
            "target_platforms": ["youtube", "tiktok"]
        }, headers=headers)
        assert task_res.status_code == 200
        task_id = task_res.json()["id"]

        # 5. Run content cycle
        run_res = await ac.post(f"/api/v1/tasks/{task_id}/run", headers=headers)
        assert run_res.status_code == 200
        cycle_data = run_res.json()
        cycle_id = cycle_data["id"]

        # 6. Check cycle preview
        preview_res = await ac.get(f"/api/v1/cycles/{cycle_id}/preview", headers=headers)
        assert preview_res.status_code == 200
        preview = preview_res.json()
        assert preview["cycle_id"] == cycle_id
        assert preview["video_url"] is not None

        # 7. Approve cycle
        approve_res = await ac.post(f"/api/v1/cycles/{cycle_id}/approve", headers=headers)
        assert approve_res.status_code == 200
        assert approve_res.json()["status"] == "published"

        # 8. Check analytics
        analytics_res = await ac.get("/api/v1/analytics", headers=headers)
        assert analytics_res.status_code == 200
        analytics = analytics_res.json()
        assert analytics["total_videos_created"] >= 1
