from typing import Any, Dict
from backend.app.agents.state import CycleState
from backend.app.core.logging import logger

async def run_caption_agent(state: CycleState) -> Dict[str, Any]:
    script = state.get("script", {})
    scenes = script.get("scenes", [])
    topic = state.get("topic", "")

    logger.info("Metadata & Tags Agent generating platform hashtags (captions disabled)")

    # Format platform hashtags
    clean_topic = topic.replace(" ", "")
    hashtags = {
        "youtube": [f"#{clean_topic}", "#Shorts", "#TechNews", "#AI", "#Automation"],
        "instagram": [f"#{clean_topic}", "#reels", "#trending", "#viral", "#tech"],
        "tiktok": [f"#{clean_topic}", "#fyp", "#tech", "#ai", "#viralvideo"]
    }

    return {
        "captions": {},
        "hashtags": hashtags,
        "current_agent": "caption_agent"
    }
