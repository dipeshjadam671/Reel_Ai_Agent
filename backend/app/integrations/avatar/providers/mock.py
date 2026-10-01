from typing import Any, Dict, List, Optional
from backend.app.integrations.avatar.base import AvatarProvider, AvatarResult
from backend.app.integrations.avatar.providers.lipsync import LipSyncAvatarProvider

class MockAvatarProvider(AvatarProvider):
    def __init__(self):
        self._engine = LipSyncAvatarProvider()

    async def generate_avatar_video(
        self,
        script_text: str,
        avatar_id: str = "avatar_alex",
        voice_id: Optional[str] = None,
        duration_seconds: Optional[float] = None,
        audio_bytes: Optional[bytes] = None,
        word_timestamps: Optional[List[Dict[str, Any]]] = None
    ) -> AvatarResult:
        return await self._engine.generate_avatar_video(
            script_text=script_text,
            avatar_id=avatar_id,
            voice_id=voice_id,
            duration_seconds=duration_seconds,
            audio_bytes=audio_bytes,
            word_timestamps=word_timestamps
        )
