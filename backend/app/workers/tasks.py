import asyncio
from celery import Celery
from backend.app.core.config import settings
from backend.app.core.logging import logger

celery_app = Celery(
    "video_ai_worker",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    worker_prefetch_multiplier=1,
)

@celery_app.task(name="execute_content_cycle_task", bind=True, max_retries=settings.MAX_CYCLE_RETRIES)
def execute_content_cycle_task(self, workspace_id: str, cycle_id: str):
    logger.info(f"Celery executing content cycle task for cycle {cycle_id}")
    from backend.app.db.session import AsyncSessionLocal
    from backend.app.workflows.content_cycle import ContentCycleWorkflow

    async def _run():
        async with AsyncSessionLocal() as session:
            workflow = ContentCycleWorkflow(session)
            await workflow.execute_cycle(workspace_id, cycle_id)
            await session.commit()

    try:
        asyncio.run(_run())
    except Exception as exc:
        logger.exception(f"Error in content cycle task {cycle_id}: {exc}")
        raise self.retry(exc=exc, countdown=10)

@celery_app.task(name="publish_video_task", bind=True)
def publish_video_task(self, workspace_id: str, cycle_id: str):
    logger.info(f"Celery publishing video for cycle {cycle_id}")
    from backend.app.db.session import AsyncSessionLocal
    from backend.app.workflows.content_cycle import ContentCycleWorkflow

    async def _run():
        async with AsyncSessionLocal() as session:
            workflow = ContentCycleWorkflow(session)
            await workflow.resume_with_approval(workspace_id, cycle_id, action="approved")
            await session.commit()

    asyncio.run(_run())
