from typing import Any, Dict
from backend.app.core.config import settings
from backend.app.integrations.publishing.base import SocialPublisher, PublicationResult
from backend.app.integrations.publishing.providers.mock import MockSocialPublisher

class InstagramPublisher(SocialPublisher):
    def __init__(self):
        self.platform = "instagram"

    async def publish(
        self,
        video_url: str,
        caption: str,
        metadata: Dict[str, Any]
    ) -> PublicationResult:
        if settings.MOCK_EXTERNAL_APIS or not settings.INSTAGRAM_APP_ID:
            return await MockSocialPublisher("instagram").publish(video_url, caption, metadata)
        return await MockSocialPublisher("instagram").publish(video_url, caption, metadata)

class TikTokPublisher(SocialPublisher):
    def __init__(self):
        self.platform = "tiktok"

    async def publish(
        self,
        video_url: str,
        caption: str,
        metadata: Dict[str, Any]
    ) -> PublicationResult:
        if settings.MOCK_EXTERNAL_APIS or not settings.TIKTOK_CLIENT_KEY:
            return await MockSocialPublisher("tiktok").publish(video_url, caption, metadata)
        return await MockSocialPublisher("tiktok").publish(video_url, caption, metadata)
