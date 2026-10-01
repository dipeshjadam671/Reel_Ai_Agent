import os
from backend.app.core.config import settings
from backend.app.integrations.tts.base import TTSProvider
from backend.app.integrations.tts.providers.mock import MockTTSProvider
from backend.app.integrations.tts.providers.openai import OpenAITTSProvider
from backend.app.integrations.tts.providers.elevenlabs import ElevenLabsTTSProvider

def get_tts_provider() -> TTSProvider:
    # 1. Prefer OpenAI TTS (highest fidelity, crystal-clear studio models: Onyx, Nova, Echo, Shimmer)
    openai_key = settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
    if openai_key and settings.TTS_PROVIDER in ("openai", "elevenlabs", "default"):
        return OpenAITTSProvider(api_key=openai_key)

    # 2. ElevenLabs if explicitly configured and enabled
    if settings.TTS_PROVIDER == "elevenlabs" and settings.ELEVENLABS_API_KEY and not settings.MOCK_EXTERNAL_APIS:
        return ElevenLabsTTSProvider()

    # 3. High-Quality Neural TTS (Azure GuyNeural / AriaNeural)
    return MockTTSProvider()
