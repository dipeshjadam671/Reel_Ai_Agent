from typing import Optional
from sqlalchemy import String, Float, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin

class Render(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin):
    __tablename__ = "renders"

    cycle_id: Mapped[str] = mapped_column(String(36), ForeignKey("cycles.id", ondelete="CASCADE"), unique=True, index=True, nullable=False)
    video_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    captions_url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    resolution: Mapped[str] = mapped_column(String(20), default="1080x1920", nullable=False)
    aspect_ratio: Mapped[str] = mapped_column(String(10), default="9:16", nullable=False)
    duration_seconds: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    file_size_bytes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    render_time_seconds: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    c2pa_manifest_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    cycle: Mapped["Cycle"] = relationship("Cycle", back_populates="render")
