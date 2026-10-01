from backend.app.integrations.publishing.base import SocialPublisher
from backend.app.integrations.publishing.providers.mock import MockSocialPublisher
from backend.app.integrations.publishing.providers.youtube import YouTubePublisher
from backend.app.integrations.publishing.providers.instagram import InstagramPublisher, TikTokPublisher

def get_publisher_for_platform(platform: str) -> SocialPublisher:
    p = platform.lower()
    if p == "youtube":
        return YouTubePublisher()
    elif p == "instagram":
        return InstagramPublisher()
    elif p == "tiktok":
        return TikTokPublisher()
    return MockSocialPublisher(platform=p)
