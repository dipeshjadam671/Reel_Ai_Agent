from typing import Optional
from sqlalchemy import String, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin

class Approval(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin):
    __tablename__ = "approvals"

    cycle_id: Mapped[str] = mapped_column(String(36), ForeignKey("cycles.id", ondelete="CASCADE"), index=True, nullable=False)
    user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action: Mapped[str] = mapped_column(String(50), nullable=False)  # "approved", "rejected", "regenerate"
    feedback: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    cycle: Mapped["Cycle"] = relationship("Cycle", back_populates="approvals")
