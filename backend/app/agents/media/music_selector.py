from typing import Any, Dict
from backend.app.agents.state import CycleState
from backend.app.core.logging import logger

async def run_music_selector(state: CycleState) -> Dict[str, Any]:
    storyboard = state.get("storyboard", {})
    mood = storyboard.get("music_mood", "upbeat_energetic")
    bpm = storyboard.get("target_bpm", 128)

    logger.info(f"Music Selector matching royalty-free soundtrack (Mood: {mood}, BPM: {bpm})")

    # In production/mock: select royalty-free track
    soundtrack = {
        "title": f"Electronic Drive ({mood})",
        "bpm": bpm,
        "mood": mood,
        "license_type": "royalty_free_commercial",
        "attribution_text": "Music: FreeSound / Royalty-Free Commercial Commons",
        "volume_duck_ratio": 0.15
    }

    return {
        "soundtrack": soundtrack,
        "current_agent": "music_selector"
    }
