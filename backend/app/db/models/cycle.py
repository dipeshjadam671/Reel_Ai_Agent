from typing import Any, Dict, Optional
from sqlalchemy import String, Float, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin
from backend.app.core.constants import CycleStatus

class Cycle(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin):
    __tablename__ = "cycles"

    workspace_id: Mapped[str] = mapped_column(String(36), ForeignKey("workspaces.id", ondelete="CASCADE"), index=True, nullable=False)
    task_id: Mapped[str] = mapped_column(String(36), ForeignKey("tasks.id", ondelete="CASCADE"), index=True, nullable=False)
    thread_id: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    status: Mapped[str] = mapped_column(String(50), default=CycleStatus.CREATED.value, nullable=False, index=True)
    current_agent: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    novelty_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    estimated_cost_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    actual_cost_usd: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    error_details: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)

    task: Mapped["Task"] = relationship("Task", back_populates="cycles")
    sources: Mapped[list["Source"]] = relationship("Source", back_populates="cycle", cascade="all, delete-orphan")
    script: Mapped[Optional["Script"]] = relationship("Script", back_populates="cycle", uselist=False, cascade="all, delete-orphan")
    assets: Mapped[list["Asset"]] = relationship("Asset", back_populates="cycle", cascade="all, delete-orphan")
    render: Mapped[Optional["Render"]] = relationship("Render", back_populates="cycle", uselist=False, cascade="all, delete-orphan")
    approvals: Mapped[list["Approval"]] = relationship("Approval", back_populates="cycle", cascade="all, delete-orphan")
    publications: Mapped[list["Publication"]] = relationship("Publication", back_populates="cycle", cascade="all, delete-orphan")

    @property
    def topic(self) -> Optional[str]:
        try:
            if self.task and self.task.topic:
                return self.task.topic
        except Exception:
            pass
        return None

    @property
    def task_name(self) -> Optional[str]:
        try:
            if self.task and self.task.name:
                return self.task.name
        except Exception:
            pass
        return None

    @property
    def reel_title(self) -> Optional[str]:
        try:
            if self.script and self.script.title:
                return self.script.title
            if self.task:
                return self.task.name or self.task.topic
        except Exception:
            pass
        return None

    @property
    def presenter_avatar_id(self) -> Optional[str]:
        try:
            if self.task and self.task.presenter_config:
                return self.task.presenter_config.get("avatar_id")
        except Exception:
            pass
        return None

    @property
    def video_url(self) -> Optional[str]:
        try:
            if self.render and self.render.video_url:
                return self.render.video_url
        except Exception:
            pass
        return None

    @property
    def thumbnail_url(self) -> Optional[str]:
        try:
            if self.render and self.render.thumbnail_url:
                return self.render.thumbnail_url
        except Exception:
            pass
        return None
