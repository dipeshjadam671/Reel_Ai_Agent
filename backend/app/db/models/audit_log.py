from typing import Any, Dict, Optional
from sqlalchemy import String, JSON, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin

class AuditLog(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin):
    __tablename__ = "audit_log"

    user_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    action: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., "CYCLE_TRIGGERED", "APPROVAL_GRANTED"
    entity_type: Mapped[str] = mapped_column(String(50), nullable=False)  # "cycle", "task", "workspace"
    entity_id: Mapped[str] = mapped_column(String(36), nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    details: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)
