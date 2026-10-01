import asyncio
import os
from typing import Any, Dict, List, Optional
import httpx
from backend.app.core.config import settings
from backend.app.core.exceptions import ProviderError
from backend.app.integrations.avatar.base import AvatarProvider, AvatarResult
from backend.app.core.logging import logger

# Map application persona IDs to real HeyGen studio avatar models
HEYGEN_AVATAR_MAP = {
    # Male
    "avatar_creator_leo": "Leos_standing_office_front",
    "avatar_tech_alex": "Edward_public_3_20240108",
    "avatar_finance_marcus": "Wayne_standing_office_front",
    "avatar_podcast_david": "Tyler_standing_office_front",
    # Female
    "avatar_anchor_sarah": "Jocelyn_standing_office_front",
    "avatar_priya_global": "Anna_public_20240108",
    "avatar_executive_elena": "Kayla_standing_office_front",
    "avatar_reporter_maya": "Monica_standing_office_front",
}

# Map gender/language to active HeyGen neural voices
HEYGEN_VOICE_MAP = {
    "male": "f43e55ae9fb540c6b62e23081c951748",    # Vincent - Thoughtful & Clear (Male)
    "female": "f415c3cd23db47c1b4fe834387d26449",  # Jocelyn - Bright & Energetic (Female)
}

class HeyGenAvatarProvider(AvatarProvider):
    def __init__(self, api_key: Optional[str] = settings.HEYGEN_API_KEY):
        self.api_key = api_key or os.getenv("HEYGEN_API_KEY")

    def _resolve_avatar(self, avatar_id: str) -> str:
        norm = str(avatar_id).lower()
        if "marcus" in norm or "finance" in norm:
            return HEYGEN_AVATAR_MAP["avatar_finance_marcus"]
        elif "david" in norm or "podcast" in norm:
            return HEYGEN_AVATAR_MAP["avatar_podcast_david"]
        elif "leo" in norm or "creator" in norm:
            return HEYGEN_AVATAR_MAP["avatar_creator_leo"]
        elif "sarah" in norm or "anchor" in norm:
            return HEYGEN_AVATAR_MAP["avatar_anchor_sarah"]
        elif "elena" in norm or "executive" in norm:
            return HEYGEN_AVATAR_MAP["avatar_executive_elena"]
        elif "maya" in norm or "reporter" in norm:
            return HEYGEN_AVATAR_MAP["avatar_reporter_maya"]
        elif "priya" in norm or "global" in norm:
            return HEYGEN_AVATAR_MAP["avatar_priya_global"]
        return HEYGEN_AVATAR_MAP["avatar_tech_alex"]

    def _resolve_voice(self, avatar_id: str) -> str:
        norm = str(avatar_id).lower()
        if any(f in norm for f in ["sarah", "priya", "elena", "maya", "female", "anna", "jocelyn", "kayla", "monica"]):
            return HEYGEN_VOICE_MAP["female"]
        return HEYGEN_VOICE_MAP["male"]

    async def generate_avatar_video(
        self,
        script_text: str,
        avatar_id: str = "avatar_alex",
        voice_id: Optional[str] = None,
        duration_seconds: Optional[float] = None,
        audio_bytes: Optional[bytes] = None,
        word_timestamps: Optional[List[Dict[str, Any]]] = None
    ) -> AvatarResult:
        if not self.api_key:
            logger.warning("No HEYGEN_API_KEY provided; falling back to video presenter engine.")
            from backend.app.integrations.avatar.providers.video_presenter import VideoPresenterAvatarProvider
            return await VideoPresenterAvatarProvider().generate_avatar_video(
                script_text, avatar_id, voice_id, duration_seconds, audio_bytes, word_timestamps
            )

        heygen_avatar = self._resolve_avatar(avatar_id)
        heygen_voice = self._resolve_voice(avatar_id)

        logger.info(f"Submitting video generation to HeyGen API (Avatar: {heygen_avatar}, Voice: {heygen_voice})")

        url = "https://api.heygen.com/v2/video/generate"
        headers = {
            "X-Api-Key": self.api_key,
            "Content-Type": "application/json"
        }
        payload = {
            "video_inputs": [
                {
                    "character": {
                        "type": "avatar",
                        "avatar_id": heygen_avatar,
                        "avatar_style": "normal"
                    },
                    "voice": {
                        "type": "text",
                        "input_text": script_text,
                        "voice_id": heygen_voice
                    },
                    "background": {
                        "type": "color",
                        "value": "#070A11"
                    }
                }
            ],
            "dimension": {"width": 1080, "height": 1920}
        }

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                res = await client.post(url, json=payload, headers=headers)
                
                # Check for 402 Insufficient credits or error responses
                if res.status_code == 402 or "insufficient_credit" in res.text:
                    logger.warning(
                        "HeyGen account balance is 0.0 (Insufficient credits). "
                        "Falling back to high-definition video presenter engine. Add credits to HeyGen to enable studio cloud rendering."
                    )
                    from backend.app.integrations.avatar.providers.video_presenter import VideoPresenterAvatarProvider
                    return await VideoPresenterAvatarProvider().generate_avatar_video(
                        script_text, avatar_id, voice_id, duration_seconds, audio_bytes, word_timestamps
                    )

                if res.status_code != 200:
                    logger.error(f"HeyGen generate error ({res.status_code}): {res.text}")
                    raise ProviderError(f"HeyGen error: {res.text}")

                data = res.json()
                video_id = data.get("data", {}).get("video_id")
                if not video_id:
                    raise ProviderError(f"No video_id returned by HeyGen: {res.text}")

                logger.info(f"HeyGen video generation initiated (video_id: {video_id}). Polling for completion...")

                # Poll status until video is rendered
                status_url = f"https://api.heygen.com/v1/video_status.get?video_id={video_id}"
                max_polls = 60  # Poll up to 3 minutes
                video_url = None

                for _ in range(max_polls):
                    await asyncio.sleep(4.0)
                    status_res = await client.get(status_url, headers={"X-Api-Key": self.api_key})
                    if status_res.status_code == 200:
                        s_data = status_res.json().get("data", {})
                        status = s_data.get("status")
                        logger.info(f"HeyGen video {video_id} status: {status}")

                        if status == "completed":
                            video_url = s_data.get("video_url")
                            break
                        elif status == "failed":
                            err_msg = s_data.get("error", "Unknown HeyGen render failure")
                            raise ProviderError(f"HeyGen video failed: {err_msg}")

                if not video_url:
                    raise ProviderError(f"HeyGen video generation timed out for {video_id}")

                logger.info(f"HeyGen video complete! Downloading from {video_url}...")
                dl_res = await client.get(video_url)
                if dl_res.status_code != 200:
                    raise ProviderError(f"Failed to download rendered HeyGen video from {video_url}")

                video_bytes = dl_res.content
                dur = duration_seconds or max(3.0, len(script_text.split()) / 2.5)

                logger.info(f"Downloaded HeyGen video: {len(video_bytes)} bytes, ~{dur:.1f}s")
                return AvatarResult(
                    video_bytes=video_bytes,
                    duration_seconds=dur,
                    format="mp4",
                    avatar_id=avatar_id,
                    has_alpha=False
                )

        except Exception as e:
            logger.warning(f"HeyGen avatar generation encountered exception: {e}. Falling back to video presenter engine.")
            from backend.app.integrations.avatar.providers.video_presenter import VideoPresenterAvatarProvider
            return await VideoPresenterAvatarProvider().generate_avatar_video(
                script_text, avatar_id, voice_id, duration_seconds, audio_bytes, word_timestamps
            )
