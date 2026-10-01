from typing import List, Optional
import httpx
from backend.app.core.config import settings
from backend.app.integrations.media.base import MediaProvider, MediaAssetItem

class PexelsMediaProvider(MediaProvider):
    def __init__(self, api_key: Optional[str] = None):
        raw_key = api_key or settings.PEXELS_API_KEY
        self.api_key = raw_key.strip("'\"") if raw_key else None

    async def search_media(
        self,
        query: str,
        asset_type: str = "video",
        count: int = 3
    ) -> List[MediaAssetItem]:
        if not self.api_key:
            from backend.app.integrations.media.providers.mock import MockMediaProvider
            return await MockMediaProvider().search_media(query, asset_type, count)

        headers = {"Authorization": self.api_key}
        endpoint = "https://api.pexels.com/videos/search" if asset_type == "video" else "https://api.pexels.com/v1/search"
        params = {"query": query, "per_page": count, "orientation": "portrait"}

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.get(endpoint, headers=headers, params=params)
                if res.status_code == 200:
                    data = res.json()
                    items = []
                    videos = data.get("videos", [])
                    for v in videos:
                        video_files = v.get("video_files", [])
                        portrait_files = [f for f in video_files if (f.get("width") or 0) < (f.get("height") or 0)]
                        target = portrait_files[0] if portrait_files else (video_files[0] if video_files else {})
                        items.append(
                            MediaAssetItem(
                                provider="pexels",
                                external_id=str(v["id"]),
                                asset_type="video",
                                media_url=target.get("link", ""),
                                thumbnail_url=v.get("image"),
                                license_type="pexels_license",
                                license_url="https://www.pexels.com/license/",
                                attribution_text=f"Video by {v.get('user', {}).get('name', 'Pexels Creator')} on Pexels",
                                duration_seconds=float(v.get("duration", 5.0))
                            )
                        )
                    if items:
                        return items
        except Exception:
            pass

        from backend.app.integrations.media.providers.mock import MockMediaProvider
        return await MockMediaProvider().search_media(query, asset_type, count)
