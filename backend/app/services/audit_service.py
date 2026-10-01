from typing import Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.models.audit_log import AuditLog
from backend.app.core.security import mask_secret

FORBIDDEN_KEYS = {"password", "token", "access_token", "refresh_token", "secret", "api_key", "secret_key"}

def sanitize_details(details: Dict[str, Any]) -> Dict[str, Any]:
    sanitized = {}
    for k, v in details.items():
        if any(fk in k.lower() for fk in FORBIDDEN_KEYS):
            sanitized[k] = mask_secret(str(v))
        elif isinstance(v, dict):
            sanitized[k] = sanitize_details(v)
        else:
            sanitized[k] = v
    return sanitized

class AuditService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def log_event(
        self,
        workspace_id: str,
        action: str,
        entity_type: str,
        entity_id: str,
        user_id: Optional[str] = None,
        ip_address: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        clean_details = sanitize_details(details or {})
        entry = AuditLog(
            workspace_id=workspace_id,
            user_id=user_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            ip_address=ip_address,
            details=clean_details
        )
        self.session.add(entry)
        await self.session.flush()
        return entry
