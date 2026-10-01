from typing import Any, Dict, List
from backend.app.agents.state import CycleState
from backend.app.integrations.media import get_media_provider
from backend.app.core.logging import logger

async def run_asset_curator(state: CycleState) -> Dict[str, Any]:
    storyboard = state.get("storyboard", {})
    scenes = storyboard.get("scenes", [])
    media_provider = get_media_provider()

    logger.info(f"Asset Curator sourcing licensed media for {len(scenes)} scenes")
    curated_assets = []

    for sc in scenes:
        query = sc.get("visual_prompt", "modern tech background")
        media_type = sc.get("media_type", "video")
        items = await media_provider.search_media(query, asset_type=media_type, count=1)
        if items:
            item = items[0]
            curated_assets.append({
                "scene_number": sc.get("scene_number"),
                "asset_type": item.asset_type,
                "provider": item.provider,
                "external_id": item.external_id,
                "storage_url": item.media_url,
                "license_type": item.license_type,
                "license_url": item.license_url,
                "attribution_text": item.attribution_text,
                "duration_seconds": item.duration_seconds
            })

    return {
        "assets": curated_assets,
        "current_agent": "asset_curator"
    }
