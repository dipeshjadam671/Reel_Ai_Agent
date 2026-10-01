import os
from backend.app.core.config import settings
from backend.app.integrations.avatar.base import AvatarProvider
from backend.app.integrations.avatar.providers.video_presenter import VideoPresenterAvatarProvider
from backend.app.integrations.avatar.providers.lipsync import LipSyncAvatarProvider
from backend.app.integrations.avatar.providers.heygen import HeyGenAvatarProvider
from backend.app.integrations.avatar.providers.did import DIDAvatarProvider

def get_avatar_provider() -> AvatarProvider:
    # 1. Check D-ID provider if key is set
    did_key = settings.DID_API_KEY or os.getenv("DID_API_KEY")
    if settings.AVATAR_PROVIDER == "did" and did_key:
        return DIDAvatarProvider(api_key=did_key)

    # 2. Check HeyGen provider if key is set and not mock
    heygen_key = settings.HEYGEN_API_KEY or os.getenv("HEYGEN_API_KEY")
    if settings.AVATAR_PROVIDER == "heygen" and heygen_key and not settings.MOCK_EXTERNAL_APIS:
        return HeyGenAvatarProvider(api_key=heygen_key)

    # 3. If HeyGen key is present, attempt HeyGen first (which falls back automatically to video presenter if credits are 0)
    if heygen_key:
        return HeyGenAvatarProvider(api_key=heygen_key)

    if did_key:
        return DIDAvatarProvider(api_key=did_key)

    # 4. Default to high-definition video presenter engine
    return VideoPresenterAvatarProvider()

