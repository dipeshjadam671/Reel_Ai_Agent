from typing import Any, Dict, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.models.preference import TaskPreference

class PreferenceService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_task_preference(self, workspace_id: str, task_id: str) -> Optional[TaskPreference]:
        stmt = select(TaskPreference).where(TaskPreference.workspace_id == workspace_id, TaskPreference.task_id == task_id)
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def set_task_preference(
        self,
        workspace_id: str,
        task_id: str,
        tone: str = "engaging",
        content_rules: Optional[Dict[str, Any]] = None,
        prohibited_keywords: Optional[list[str]] = None
    ) -> TaskPreference:
        pref = await self.get_task_preference(workspace_id, task_id)
        if not pref:
            pref = TaskPreference(
                workspace_id=workspace_id,
                task_id=task_id,
                tone_of_voice=tone,
                content_rules=content_rules or {},
                prohibited_keywords=prohibited_keywords or [],
                compliance_overrides={}
            )
            self.session.add(pref)
        else:
            pref.tone_of_voice = tone
            pref.content_rules = content_rules or {}
            pref.prohibited_keywords = prohibited_keywords or []
        await self.session.flush()
        return pref
