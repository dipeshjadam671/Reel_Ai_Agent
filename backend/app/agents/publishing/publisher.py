from datetime import datetime, timezone
from typing import Any, Dict, List
from backend.app.agents.state import CycleState
from backend.app.integrations.publishing import get_publisher_for_platform
from backend.app.core.logging import logger

async def run_publisher(state: CycleState) -> Dict[str, Any]:
    render = state.get("render", {})
    script = state.get("script", {})
    platforms = state.get("platforms", ["youtube"])
    video_url = render.get("video_url", "")
    title = script.get("title", "Autonomous Video")
    hook = script.get("hook", "")
    hashtags_map = state.get("hashtags", {})

    logger.info(f"Publisher Agent deploying video to platforms: {platforms}")
    publications = []

    for platform in platforms:
        pub = get_publisher_for_platform(platform)
        tags = " ".join(hashtags_map.get(platform, ["#Shorts", "#AI"]))
        caption = f"{title}\n\n{hook}\n\n{tags}"
        metadata = {
            "title": title,
            "description": caption,
            "privacy_status": "public",
            "made_for_kids": False,
        }

        result = await pub.publish(video_url=video_url, caption=caption, metadata=metadata)
        publications.append({
            "platform": platform,
            "status": result.status,
            "platform_post_id": result.platform_post_id,
            "permalink": result.permalink,
            "published_at": datetime.now(timezone.utc).isoformat(),
            "metadata_payload": metadata,
            "error_message": result.error
        })
        logger.info(f"Published to {platform}: {result.permalink}")

    return {
        "publications": publications,
        "current_agent": "publisher"
    }
