from typing import Any, Dict
from sqlalchemy import String, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin

class TaskPreference(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin):
    __tablename__ = "task_preferences"

    task_id: Mapped[str] = mapped_column(String(36), ForeignKey("tasks.id", ondelete="CASCADE"), index=True, nullable=False)
    tone_of_voice: Mapped[str] = mapped_column(String(100), default="informative_engaging", nullable=False)
    content_rules: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    prohibited_keywords: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    compliance_overrides: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
