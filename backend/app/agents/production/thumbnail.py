from typing import Any, Dict
from backend.app.agents.state import CycleState
from backend.app.core.logging import logger

async def run_thumbnail_agent(state: CycleState) -> Dict[str, Any]:
    script = state.get("script", {})
    title = script.get("title", state.get("topic", "AI Video"))

    logger.info(f"Thumbnail Agent drafting overlay typography for: '{title}'")

    return {
        "thumbnail_metadata": {
            "title_overlay": title,
            "badge_color": "#EF4444",
            "frame_timestamp": 1.0
        },
        "current_agent": "thumbnail_agent"
    }
