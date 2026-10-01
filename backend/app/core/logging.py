import json
import logging
import sys
from contextvars import ContextVar
from datetime import datetime, timezone
from typing import Any, Dict, Optional
from backend.app.core.config import settings

# Context variables for tracing
ctx_workspace_id: ContextVar[Optional[str]] = ContextVar("ctx_workspace_id", default=None)
ctx_task_id: ContextVar[Optional[str]] = ContextVar("ctx_task_id", default=None)
ctx_cycle_id: ContextVar[Optional[str]] = ContextVar("ctx_cycle_id", default=None)
ctx_thread_id: ContextVar[Optional[str]] = ContextVar("ctx_thread_id", default=None)
ctx_agent: ContextVar[Optional[str]] = ContextVar("ctx_agent", default=None)

class StructuredJsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_obj: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "workspace_id": ctx_workspace_id.get(),
            "task_id": ctx_task_id.get(),
            "cycle_id": ctx_cycle_id.get(),
            "thread_id": ctx_thread_id.get(),
            "agent": ctx_agent.get(),
        }

        # Include custom extra fields if provided
        for key in ["event", "status", "duration", "cost"]:
            if hasattr(record, key):
                log_obj[key] = getattr(record, key)

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_obj)

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredJsonFormatter())
        logger.addHandler(handler)
        logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
        logger.propagate = False
    return logger

logger = get_logger("video_ai_platform")
