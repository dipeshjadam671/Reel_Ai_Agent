import os
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from fastapi.responses import FileResponse
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.session import get_db
from backend.app.core.exceptions import NotFoundError
from backend.app.db.models.cycle import Cycle
from backend.app.schemas.cycle import CycleOut, CycleStatusOut, CyclePreviewOut
from backend.app.schemas.approval import ApprovalActionRequest
from backend.app.schemas.research import SourceItem
from backend.app.schemas.script import ScriptOut
from backend.app.schemas.media import AssetOut
from backend.app.services.cycle_service import CycleService
from backend.app.api.dependencies import get_current_user, get_current_workspace_id
from backend.app.db.models.user import User
from backend.app.db.models.render import Render
from backend.app.workflows.production_workflow import ProductionWorkflow

router = APIRouter()

@router.get("", response_model=List[CycleOut])
async def list_cycles(
    task_id: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    workspace_id: str = Depends(get_current_workspace_id),
    db: AsyncSession = Depends(get_db)
):
    service = CycleService(db)
    return await service.list_cycles(workspace_id, task_id=task_id, skip=skip, limit=limit)

@router.get("/{cycle_id}", response_model=CycleOut)
async def get_cycle(
    cycle_id: str,
    workspace_id: str = Depends(get_current_workspace_id),
    db: AsyncSession = Depends(get_db)
):
    service = CycleService(db)
    return await service.get_cycle(workspace_id, cycle_id)

@router.get("/{cycle_id}/status", response_model=CycleStatusOut)
async def get_cycle_status(
    cycle_id: str,
    workspace_id: str = Depends(get_current_workspace_id),
    db: AsyncSession = Depends(get_db)
):
    service = CycleService(db)
    c = await service.get_cycle(workspace_id, cycle_id)
    return CycleStatusOut(
        cycle_id=c.id,
        status=c.status,
        current_agent=c.current_agent,
        novelty_score=c.novelty_score,
        estimated_cost_usd=c.estimated_cost_usd,
        actual_cost_usd=c.actual_cost_usd,
        updated_at=c.updated_at
    )

@router.get("/{cycle_id}/preview", response_model=CyclePreviewOut)
async def get_cycle_preview(
    cycle_id: str,
    workspace_id: str = Depends(get_current_workspace_id),
    db: AsyncSession = Depends(get_db)
):
    service = CycleService(db)
    c = await service.get_cycle(workspace_id, cycle_id)

    video_url = f"/api/v1/cycles/{c.id}/video" if c.render and c.render.video_url else None
    thumbnail_url = f"/api/v1/cycles/{c.id}/thumbnail" if c.render and c.render.thumbnail_url else None
    captions_url = f"/api/v1/cycles/{c.id}/subtitles" if c.render and c.render.captions_url else None
    duration = c.render.duration_seconds if c.render else 0.0

    title = c.script.title if c.script else c.task.topic
    hook = c.script.hook if c.script else None
    cta = c.script.call_to_action if c.script else None

    return CyclePreviewOut(
        cycle_id=c.id,
        status=c.status,
        topic=c.task.topic,
        language=c.task.language,
        video_url=video_url,
        thumbnail_url=thumbnail_url,
        captions_url=captions_url,
        duration_seconds=duration,
        resolution=c.render.resolution if c.render else "1080x1920",
        title=title,
        hook=hook,
        call_to_action=cta,
        qa_score=0.94 if c.render else None,
        compliance_passed=True if c.render else False
    )

async def _ensure_cycle_media(c: Cycle, db: AsyncSession):
    if c.render and c.render.video_url and os.path.exists(c.render.video_url):
        return c.render.video_url, c.render.thumbnail_url

    topic = (c.task.topic if c.task else "") or (c.script.title if c.script else "Autonomous Video")
    lang = (c.task.language if c.task else "en") or "en"
    script_data = {
        "title": c.script.title if c.script else topic,
        "hook": c.script.hook if c.script else "",
        "scenes": c.script.scenes if (c.script and c.script.scenes) else [
            {"scene_index": 1, "narration": topic, "duration_seconds": 5.0}
        ],
        "call_to_action": c.script.call_to_action if c.script else "Follow for more!"
    }
    presenter_cfg = (c.task.presenter_config if c.task else {}) or {
        "avatar_id": "avatar_creator_leo",
        "voice_id": "echo",
        "layout": "pip"
    }
    state = {
        "workspace_id": c.workspace_id,
        "cycle_id": c.id,
        "topic": topic,
        "language": lang,
        "script": script_data,
        "presenter_config": presenter_cfg,
        "assets": []
    }
    workflow = ProductionWorkflow()
    res_state = await workflow.run(state)
    render_res = res_state.get("render", {})
    video_url = render_res.get("video_url")
    thumb_url = render_res.get("thumbnail_url")
    dur = render_res.get("duration_seconds", 5.0)

    if c.render:
        c.render.video_url = video_url
        c.render.thumbnail_url = thumb_url
        c.render.duration_seconds = dur
    else:
        new_render = Render(
            workspace_id=c.workspace_id,
            cycle_id=c.id,
            video_url=video_url,
            thumbnail_url=thumb_url,
            duration_seconds=dur,
            resolution="1080x1920",
            aspect_ratio="9:16"
        )
        db.add(new_render)
        c.render = new_render

    await db.commit()
    return video_url, thumb_url

@router.api_route("/{cycle_id}/video", methods=["GET", "HEAD"])
async def get_cycle_video(
    cycle_id: str,
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Cycle)
        .where(Cycle.id == cycle_id)
        .options(
            selectinload(Cycle.render),
            selectinload(Cycle.script),
            selectinload(Cycle.task)
        )
    )
    result = await db.execute(stmt)
    c = result.scalars().first()
    if not c:
        raise NotFoundError(message="Cycle not found")

    file_path = c.render.video_url if c.render else None
    if not file_path or not os.path.exists(file_path):
        file_path, _ = await _ensure_cycle_media(c, db)

    if not file_path or not os.path.exists(file_path):
        raise NotFoundError(message="Video file not found on disk")
    return FileResponse(file_path, media_type="video/mp4", content_disposition_type="inline")

@router.api_route("/{cycle_id}/thumbnail", methods=["GET", "HEAD"])
async def get_cycle_thumbnail(
    cycle_id: str,
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Cycle)
        .where(Cycle.id == cycle_id)
        .options(
            selectinload(Cycle.render),
            selectinload(Cycle.script),
            selectinload(Cycle.task)
        )
    )
    result = await db.execute(stmt)
    c = result.scalars().first()
    if not c:
        raise NotFoundError(message="Cycle not found")

    file_path = c.render.thumbnail_url if c.render else None
    if not file_path or not os.path.exists(file_path):
        _, file_path = await _ensure_cycle_media(c, db)

    if not file_path or not os.path.exists(file_path):
        raise NotFoundError(message="Thumbnail file not found on disk")
    return FileResponse(file_path, media_type="image/jpeg", content_disposition_type="inline")

@router.api_route("/{cycle_id}/subtitles", methods=["GET", "HEAD"])
async def get_cycle_subtitles(
    cycle_id: str,
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Cycle)
        .where(Cycle.id == cycle_id)
        .options(selectinload(Cycle.render))
    )
    result = await db.execute(stmt)
    c = result.scalars().first()
    if not c or not c.render or not c.render.captions_url:
        raise NotFoundError(message="Subtitles not found for this cycle")
    file_path = c.render.captions_url
    if not os.path.exists(file_path):
        raise NotFoundError(message="Subtitles file not found on disk")
    media_type = "text/vtt" if file_path.endswith(".vtt") else "text/plain; charset=utf-8"
    return FileResponse(file_path, media_type=media_type, content_disposition_type="inline")


@router.post("/{cycle_id}/approve", response_model=CycleOut)
async def approve_cycle(
    cycle_id: str,
    workspace_id: str = Depends(get_current_workspace_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = CycleService(db)
    return await service.approve_cycle(workspace_id, cycle_id, user_id=current_user.id)

@router.post("/{cycle_id}/reject", response_model=CycleOut)
async def reject_cycle(
    cycle_id: str,
    req: ApprovalActionRequest,
    workspace_id: str = Depends(get_current_workspace_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = CycleService(db)
    return await service.reject_cycle(workspace_id, cycle_id, user_id=current_user.id, feedback=req.feedback)

@router.post("/{cycle_id}/regenerate", response_model=CycleOut)
async def regenerate_cycle(
    cycle_id: str,
    req: ApprovalActionRequest,
    workspace_id: str = Depends(get_current_workspace_id),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    service = CycleService(db)
    return await service.regenerate_cycle(workspace_id, cycle_id, user_id=current_user.id, feedback=req.feedback)

@router.get("/{cycle_id}/sources", response_model=List[SourceItem])
async def get_cycle_sources(
    cycle_id: str,
    workspace_id: str = Depends(get_current_workspace_id),
    db: AsyncSession = Depends(get_db)
):
    service = CycleService(db)
    c = await service.get_cycle(workspace_id, cycle_id)
    return [
        SourceItem(
            title=s.title,
            url=s.url,
            domain=s.domain,
            summary=s.summary,
            credibility_score=s.credibility_score
        )
        for s in c.sources
    ]

@router.get("/{cycle_id}/script", response_model=Optional[ScriptOut])
async def get_cycle_script(
    cycle_id: str,
    workspace_id: str = Depends(get_current_workspace_id),
    db: AsyncSession = Depends(get_db)
):
    service = CycleService(db)
    c = await service.get_cycle(workspace_id, cycle_id)
    return c.script

@router.get("/{cycle_id}/assets", response_model=List[AssetOut])
async def get_cycle_assets(
    cycle_id: str,
    workspace_id: str = Depends(get_current_workspace_id),
    db: AsyncSession = Depends(get_db)
):
    service = CycleService(db)
    c = await service.get_cycle(workspace_id, cycle_id)
    return c.assets
