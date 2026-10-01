from typing import Optional
from sqlalchemy import String, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin

class Asset(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin):
    __tablename__ = "assets"

    cycle_id: Mapped[str] = mapped_column(String(36), ForeignKey("cycles.id", ondelete="CASCADE"), index=True, nullable=False)
    asset_type: Mapped[str] = mapped_column(String(50), nullable=False)  # "video", "image", "audio", "avatar"
    provider: Mapped[str] = mapped_column(String(100), nullable=False)   # "pexels", "unsplash", "elevenlabs", "heygen", "mock"
    external_id: Mapped[str] = mapped_column(String(255), nullable=False)
    storage_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    license_type: Mapped[str] = mapped_column(String(100), default="commercial_use_allowed", nullable=False)
    license_url: Mapped[Optional[str]] = mapped_column(String(2048), nullable=True)
    attribution_text: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    duration_seconds: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    cycle: Mapped["Cycle"] = relationship("Cycle", back_populates="assets")
