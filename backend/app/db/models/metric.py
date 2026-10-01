from sqlalchemy import String, Integer, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin

class Metric(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin):
    __tablename__ = "post_metrics"

    publication_id: Mapped[str] = mapped_column(String(36), ForeignKey("publications.id", ondelete="CASCADE"), index=True, nullable=False)
    views: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    likes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    shares: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    comments: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    retention_rate_pct: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    watch_time_seconds: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)

    publication: Mapped["Publication"] = relationship("Publication", back_populates="metrics")
