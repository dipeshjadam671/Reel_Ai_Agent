from typing import Any, Dict, List, Optional
from sqlalchemy import String, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin
from backend.app.core.constants import TaskStatus

class Task(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin):
    __tablename__ = "tasks"

    workspace_id: Mapped[str] = mapped_column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    topic: Mapped[str] = mapped_column(String(500), nullable=False)
    seed_script: Mapped[Optional[str]] = mapped_column(String(5000), nullable=True)
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    target_platforms: Mapped[List[str]] = mapped_column(JSON, default=list, nullable=False)
    presenter_config: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    schedule_config: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    brand_preferences: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default=TaskStatus.ACTIVE.value, nullable=False)

    workspace: Mapped["Workspace"] = relationship("Workspace", back_populates="tasks")
    cycles: Mapped[list["Cycle"]] = relationship("Cycle", back_populates="task", cascade="all, delete-orphan")

    @property
    def latest_cycle(self) -> Optional[Any]:
        try:
            if self.cycles:
                return sorted(self.cycles, key=lambda c: c.created_at, reverse=True)[0]
        except Exception:
            pass
        return None

    @property
    def latest_cycle_id(self) -> Optional[str]:
        lc = self.latest_cycle
        return lc.id if lc else None

    @property
    def latest_cycle_status(self) -> Optional[str]:
        lc = self.latest_cycle
        return lc.status if lc else None
