from typing import Any, Dict, Optional, Protocol, runtime_checkable
from pydantic import BaseModel

class PublicationResult(BaseModel):
    platform: str
    status: str  # "published", "failed", "pending"
    platform_post_id: Optional[str] = None
    permalink: Optional[str] = None
    error: Optional[str] = None

@runtime_checkable
class SocialPublisher(Protocol):
    async def publish(
        self,
        video_url: str,
        caption: str,
        metadata: Dict[str, Any]
    ) -> PublicationResult:
        ...
