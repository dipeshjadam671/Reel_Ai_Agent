from backend.app.workers.tasks import celery_app
from backend.app.core.logging import logger

@celery_app.task(name="async_research_task")
def async_research_task(workspace_id: str, topic: str):
    logger.info(f"Research worker processing topic: {topic}")
    return {"status": "success", "topic": topic}
