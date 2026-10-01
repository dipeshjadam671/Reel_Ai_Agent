from typing import Any, Dict, List
from sqlalchemy import String, JSON, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin

class Script(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin):
    __tablename__ = "scripts"

    cycle_id: Mapped[str] = mapped_column(String(36), ForeignKey("cycles.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    hook: Mapped[str] = mapped_column(Text, nullable=False)
    raw_content: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(String(10), default="en", nullable=False)
    scenes: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    claims: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
    call_to_action: Mapped[str] = mapped_column(String(500), nullable=False)
    version: Mapped[int] = mapped_column(default=1, nullable=False)

    cycle: Mapped["Cycle"] = relationship("Cycle", back_populates="script")
