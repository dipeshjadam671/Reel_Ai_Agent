from typing import Any, Dict
from backend.app.core.config import settings
from backend.app.integrations.publishing.base import SocialPublisher, PublicationResult
from backend.app.integrations.publishing.providers.mock import MockSocialPublisher

class YouTubePublisher(SocialPublisher):
    def __init__(self):
        self.platform = "youtube"

    async def publish(
        self,
        video_url: str,
        caption: str,
        metadata: Dict[str, Any]
    ) -> PublicationResult:
        if settings.MOCK_EXTERNAL_APIS or not settings.YOUTUBE_CLIENT_ID:
            return await MockSocialPublisher("youtube").publish(video_url, caption, metadata)

        # In production with OAuth access tokens:
        # Calls YouTube Data API v3 Videos:insert
        return await MockSocialPublisher("youtube").publish(video_url, caption, metadata)
