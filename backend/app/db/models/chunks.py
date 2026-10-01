from typing import Any, Dict, List, Optional
from sqlalchemy import String, Text, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from backend.app.db.base import Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin

class DocChunk(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin):
    __tablename__ = "doc_chunks"

    source_url: Mapped[str] = mapped_column(String(2048), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[Optional[List[float]]] = mapped_column(JSON, nullable=True)  # Stored as vector/JSON
    chunk_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, default=dict, nullable=False)

class ScriptChunk(Base, UUIDPrimaryKeyMixin, TimestampMixin, TenantScopedMixin):
    __tablename__ = "script_chunks"

    cycle_id: Mapped[str] = mapped_column(String(36), ForeignKey("cycles.id", ondelete="CASCADE"), index=True, nullable=False)
    topic: Mapped[str] = mapped_column(String(500), nullable=False)
    hook: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[Optional[List[float]]] = mapped_column(JSON, nullable=True)
    claims: Mapped[List[Dict[str, Any]]] = mapped_column(JSON, default=list, nullable=False)
