from typing import Any, Dict, List, Optional, Protocol, runtime_checkable
from pydantic import BaseModel

class AvatarResult(BaseModel):
    video_bytes: bytes
    duration_seconds: float
    format: str = "mp4"
    avatar_id: str
    has_alpha: bool = False

@runtime_checkable
class AvatarProvider(Protocol):
    async def generate_avatar_video(
        self,
        script_text: str,
        avatar_id: str = "avatar_alex",
        voice_id: Optional[str] = None,
        duration_seconds: Optional[float] = None,
        audio_bytes: Optional[bytes] = None,
        word_timestamps: Optional[List[Dict[str, Any]]] = None
    ) -> AvatarResult:
        ...

