from datetime import datetime
from typing import Any, Dict, Optional
from sqlalchemy import String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin

class Publication(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin):
    __tablename__ = "publications"

    cycle_id: Mapped[str] = mapped_column(String(36), ForeignKey("cycles.id", ondelete="CASCADE"), index=True, nullable=False)
    platform: Mapped[str] = mapped_column(String(50), nullable=False)  # "youtube", "instagram", "tiktok"
    status: Mapped[str] = mapped_column(String(50), default="pending", nullable=False)  # "pending", "published", "failed"
    platform_post_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    permalink: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    metadata_payload: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    cycle: Mapped["Cycle"] = relationship("Cycle", back_populates="publications")
    metrics: Mapped[list["Metric"]] = relationship("Metric", back_populates="publication", cascade="all, delete-orphan")
