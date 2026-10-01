from typing import List, Optional, Protocol, runtime_checkable
from pydantic import BaseModel

class MediaAssetItem(BaseModel):
    provider: str
    external_id: str
    asset_type: str  # "video" or "image"
    media_url: str
    thumbnail_url: Optional[str] = None
    license_type: str = "commercial_use_allowed"
    license_url: str = "https://www.pexels.com/license/"
    attribution_text: str = "Provided by Pexels / Verified Stock"
    duration_seconds: Optional[float] = 5.0

@runtime_checkable
class MediaProvider(Protocol):
    async def search_media(
        self,
        query: str,
        asset_type: str = "video",
        count: int = 3
    ) -> List[MediaAssetItem]:
        ...
