import uuid
from typing import Any, Dict
from backend.app.integrations.publishing.base import SocialPublisher, PublicationResult

class MockSocialPublisher(SocialPublisher):
    def __init__(self, platform: str = "youtube"):
        self.platform = platform

    async def publish(
        self,
        video_url: str,
        caption: str,
        metadata: Dict[str, Any]
    ) -> PublicationResult:
        mock_id = f"mock_{uuid.uuid4().hex[:10]}"
        permalinks = {
            "youtube": f"https://youtube.com/shorts/{mock_id}",
            "instagram": f"https://instagram.com/reel/{mock_id}",
            "tiktok": f"https://tiktok.com/@creator/video/{mock_id}"
        }
        permalink = permalinks.get(self.platform, f"https://social.example.com/{self.platform}/{mock_id}")
        return PublicationResult(
            platform=self.platform,
            status="published",
            platform_post_id=mock_id,
            permalink=permalink
        )
