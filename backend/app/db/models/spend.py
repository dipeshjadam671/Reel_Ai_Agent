from typing import Optional
from sqlalchemy import String, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin

class SpendLedger(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin):
    __tablename__ = "spend_ledger"

    cycle_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("cycles.id", ondelete="SET NULL"), index=True, nullable=True)
    provider: Mapped[str] = mapped_column(String(100), nullable=False)   # "openai", "elevenlabs", "heygen", "mock"
    operation: Mapped[str] = mapped_column(String(100), nullable=False)  # "script_generation", "tts_synthesis", "avatar_render"
    units: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    unit_cost: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    idempotency_key: Mapped[Optional[str]] = mapped_column(String(255), unique=True, index=True, nullable=True)
