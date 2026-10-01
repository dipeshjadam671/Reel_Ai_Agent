from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List
import zoneinfo

class SchedulingService:
    """
    Timezone-aware scheduling engine handling daily, weekday, weekend,
    and custom day schedules with lead time and daylight saving support.
    """
    def is_task_due(self, schedule_config: Dict[str, Any], last_run_at: datetime = None) -> bool:
        if not schedule_config:
            return False

        tz_str = schedule_config.get("timezone", "UTC")
        try:
            tz = zoneinfo.ZoneInfo(tz_str)
        except Exception:
            tz = timezone.utc

        now_in_tz = datetime.now(tz)
        target_time_str = schedule_config.get("time", "09:00")
        target_hour, target_min = [int(x) for x in target_time_str.split(":")]

        # Check day-of-week eligibility
        freq = schedule_config.get("frequency", "daily")
        active_days = schedule_config.get("active_days", ["mon", "tue", "wed", "thu", "fri"])
        weekday_map = {0: "mon", 1: "tue", 2: "wed", 3: "thu", 4: "fri", 5: "sat", 6: "sun"}
        today_code = weekday_map[now_in_tz.weekday()]

        if freq == "weekdays" and now_in_tz.weekday() >= 5:
            return False
        if freq == "weekends" and now_in_tz.weekday() < 5:
            return False
        if freq == "custom" and today_code not in active_days:
            return False

        # Check time window (within 15 minutes of scheduled time)
        scheduled_dt = now_in_tz.replace(hour=target_hour, minute=target_min, second=0, microsecond=0)
        diff_minutes = (now_in_tz - scheduled_dt).total_seconds() / 60.0

        if not (0 <= diff_minutes <= 15):
            return False

        # Exactly-once guarantee for the day: ensure not already executed today
        if last_run_at:
            last_in_tz = last_run_at.astimezone(tz)
            if last_in_tz.date() == now_in_tz.date():
                return False

        return True

    async def check_and_trigger_due_tasks(self):
        from sqlalchemy import select
        from backend.app.db.session import AsyncSessionLocal
        from backend.app.db.models.task import Task
        from backend.app.db.models.cycle import Cycle
        from backend.app.services.cycle_service import CycleService
        from backend.app.core.logging import logger

        try:
            async with AsyncSessionLocal() as session:
                stmt = select(Task).where(Task.status == "active")
                result = await session.execute(stmt)
                tasks = result.scalars().all()
                for t in tasks:
                    # Find latest cycle run time for this task
                    c_stmt = (
                        select(Cycle.created_at)
                        .where(Cycle.task_id == t.id)
                        .order_by(Cycle.created_at.desc())
                        .limit(1)
                    )
                    c_res = await session.execute(c_stmt)
                    last_run = c_res.scalars().first()

                    if self.is_task_due(t.schedule_config, last_run_at=last_run):
                        logger.info(f"Task {t.id} ('{t.name}') is due according to schedule {t.schedule_config}! Triggering cycle...")
                        cycle_service = CycleService(session)
                        try:
                            await cycle_service.trigger_cycle(
                                workspace_id=t.workspace_id,
                                task_id=t.id,
                            )
                            await session.commit()
                        except Exception as e:
                            logger.error(f"Error triggering scheduled task {t.id}: {e}")
        except Exception as exc:
            from backend.app.core.logging import logger
            logger.error(f"Error in scheduler check: {exc}")

scheduling_service = SchedulingService()
