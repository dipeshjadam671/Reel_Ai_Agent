from typing import Any, Dict, Optional
from sqlalchemy import String, Float, JSON, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin

class Source(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin):
    __tablename__ = "sources"

    cycle_id: Mapped[str] = mapped_column(String(36), ForeignKey("cycles.id", ondelete="CASCADE"), index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    url: Mapped[str] = mapped_column(String(2048), nullable=False)
    domain: Mapped[str] = mapped_column(String(255), nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    claims: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    credibility_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)

    cycle: Mapped["Cycle"] = relationship("Cycle", back_populates="sources")
