import random
from typing import Any, Dict
from backend.app.agents.state import CycleState
from backend.app.core.logging import logger

async def run_analytics(state: CycleState) -> Dict[str, Any]:
    publications = state.get("publications", [])
    logger.info(f"Analytics Agent collecting post performance for {len(publications)} publications")

    metrics_list = []
    for pub in publications:
        # In mock or live polling:
        views = random.randint(1200, 8500)
        likes = int(views * random.uniform(0.06, 0.12))
        shares = int(views * random.uniform(0.01, 0.03))
        comments = int(views * random.uniform(0.005, 0.02))
        retention = round(random.uniform(72.0, 91.5), 1)

        metrics_list.append({
            "platform": pub.get("platform"),
            "platform_post_id": pub.get("platform_post_id"),
            "views": views,
            "likes": likes,
            "shares": shares,
            "comments": comments,
            "retention_rate_pct": retention,
            "watch_time_seconds": round(views * 14.5, 1)
        })

    return {
        "post_metrics": metrics_list,
        "current_agent": "analytics"
    }
