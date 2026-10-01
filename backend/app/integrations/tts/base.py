from typing import Any, Dict, List, Optional, Protocol, runtime_checkable
from pydantic import BaseModel

class TTSResult(BaseModel):
    audio_bytes: bytes
    duration_seconds: float
    format: str = "mp3"
    word_timestamps: List[Dict[str, Any]] = []

@runtime_checkable
class TTSProvider(Protocol):
    async def generate(
        self,
        text: str,
        language: str = "en",
        voice: Optional[str] = None
    ) -> TTSResult:
        ...
