from typing import Any, Dict
from backend.app.agents.state import CycleState
from backend.app.integrations.tts import get_tts_provider
from backend.app.integrations.storage import get_storage_provider
from backend.app.core.logging import logger

async def run_voice_agent(state: CycleState) -> Dict[str, Any]:
    script = state.get("script", {})
    presenter_cfg = state.get("presenter_config", {})
    language = state.get("language", "en")
    avatar_id = str(presenter_cfg.get("avatar_id", "")).lower()
    voice_id = presenter_cfg.get("voice_id")

    # Smart voice mapping for premium broadcast audio matching presenter gender and personality
    if not voice_id or voice_id in ("voice_en_neutral", "default", "21m00Tcm4TlvDq8ikWAM", "AZnzlk1XvdvUeBnXmlld", "EXAVITQu4vr4xnSDxMaL"):
        # Female presenters
        if any(f in avatar_id for f in ["sarah", "anchor"]):
            voice_id = "nova"
        elif any(f in avatar_id for f in ["priya", "global"]):
            voice_id = "hi-IN-SwaraNeural" if language.startswith("hi") else "shimmer"
        elif any(f in avatar_id for f in ["elena", "executive"]):
            voice_id = "alloy"
        elif any(f in avatar_id for f in ["maya", "reporter"]):
            voice_id = "shimmer"
        elif "female" in avatar_id:
            voice_id = "nova"
        # Male presenters
        elif any(f in avatar_id for f in ["marcus", "finance"]):
            voice_id = "echo"
        elif any(f in avatar_id for f in ["david", "podcast", "investigative"]):
            voice_id = "onyx"
        elif any(f in avatar_id for f in ["leo", "creator"]):
            voice_id = "fable"
        else:
            voice_id = "onyx"

    full_voiceover = " ".join([sc.get("voiceover_text", "") for sc in script.get("scenes", [])]).strip()
    if not full_voiceover:
        full_voiceover = f"{script.get('hook', '')} {script.get('call_to_action', '')}".strip() or "Welcome to this episode."
    logger.info(f"Voice Agent generating speech synthesis ({len(full_voiceover.split())} words in {language})")

    tts = get_tts_provider()
    tts_result = await tts.generate(text=full_voiceover, language=language, voice=voice_id)

    storage = get_storage_provider()
    cycle_id = state.get("cycle_id", "temp")
    audio_url = await storage.save_file(
        tts_result.audio_bytes,
        f"cycles/{cycle_id}/voiceover.{tts_result.format}",
        "audio/wav" if tts_result.format == "wav" else "audio/mpeg"
    )

    return {
        "voice_track": {
            "storage_url": audio_url,
            "duration_seconds": tts_result.duration_seconds,
            "format": tts_result.format,
            "word_timestamps": tts_result.word_timestamps,
            "_raw_bytes": tts_result.audio_bytes  # Kept in pipeline context for rendering
        },
        "current_agent": "voice_agent"
    }
