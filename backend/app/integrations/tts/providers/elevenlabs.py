import io
from typing import Optional
import httpx
from backend.app.core.config import settings
from backend.app.core.exceptions import ProviderError
from backend.app.integrations.tts.base import TTSProvider, TTSResult

class ElevenLabsTTSProvider(TTSProvider):
    def __init__(self, api_key: Optional[str] = settings.ELEVENLABS_API_KEY):
        self.api_key = api_key
        self.voice_id = settings.ELEVENLABS_DEFAULT_VOICE_ID

    async def generate(
        self,
        text: str,
        language: str = "en",
        voice: Optional[str] = None
    ) -> TTSResult:
        if not self.api_key:
            from backend.app.integrations.tts.providers.mock import MockTTSProvider
            return await MockTTSProvider().generate(text, language, voice)

        voice_target = voice or self.voice_id
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_target}/with-timestamps"
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
        }

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                res = await client.post(url, json=payload, headers=headers)
                if res.status_code != 200:
                    raise ProviderError(f"ElevenLabs TTS error: {res.text}")
                audio_bytes = res.content
                words = text.split()
                duration = max(2.0, len(words) / 2.5)
                return TTSResult(
                    audio_bytes=audio_bytes,
                    duration_seconds=duration,
                    format="mp3",
                    word_timestamps=[]
                )
        except Exception as e:
            if isinstance(e, ProviderError):
                raise
            from backend.app.integrations.tts.providers.mock import MockTTSProvider
            return await MockTTSProvider().generate(text, language, voice)
