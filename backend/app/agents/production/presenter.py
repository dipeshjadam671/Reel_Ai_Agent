from typing import Any, Dict
from backend.app.agents.state import CycleState
from backend.app.integrations.avatar import get_avatar_provider
from backend.app.integrations.storage import get_storage_provider
from backend.app.core.logging import logger

async def run_presenter_agent(state: CycleState) -> Dict[str, Any]:
    script = state.get("script", {})
    presenter_cfg = state.get("presenter_config", {})
    avatar_id = presenter_cfg.get("avatar_id", "avatar_alex")
    voice_track = state.get("voice_track", {})
    duration = voice_track.get("duration_seconds", 12.0)

    logger.info(f"Presenter Agent generating avatar video clip (Avatar: {avatar_id}, Duration: {duration}s)")

    avatar_provider = get_avatar_provider()
    
    # Extract full spoken voiceover text to match audio track
    full_voiceover = " ".join([sc.get("voiceover_text", "") for sc in script.get("scenes", [])]).strip()
    if not full_voiceover:
        full_voiceover = f"{script.get('hook', '')} {script.get('call_to_action', '')}".strip() or "Welcome to this episode."

    avatar_res = await avatar_provider.generate_avatar_video(
        script_text=full_voiceover,
        avatar_id=avatar_id,
        duration_seconds=duration,
        audio_bytes=voice_track.get("_raw_bytes"),
        word_timestamps=voice_track.get("word_timestamps")
    )

    storage = get_storage_provider()
    cycle_id = state.get("cycle_id", "temp")
    avatar_url = await storage.save_file(
        avatar_res.video_bytes,
        f"cycles/{cycle_id}/avatar_presenter.mp4",
        "video/mp4"
    )

    return {
        "presenter_clips": [
            {
                "avatar_id": avatar_id,
                "storage_url": avatar_url,
                "duration_seconds": avatar_res.duration_seconds,
                "_raw_bytes": avatar_res.video_bytes
            }
        ],
        "current_agent": "presenter_agent"
    }
