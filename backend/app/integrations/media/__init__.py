from backend.app.core.config import settings
from backend.app.integrations.media.base import MediaProvider
from backend.app.integrations.media.providers.mock import MockMediaProvider
from backend.app.integrations.media.providers.pexels import PexelsMediaProvider

def get_media_provider() -> MediaProvider:
    if settings.PEXELS_API_KEY and settings.PEXELS_API_KEY.strip("'\""):
        return PexelsMediaProvider()
    return MockMediaProvider()

