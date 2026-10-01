import asyncio
import base64
import os
from typing import Any, Dict, List, Optional
import httpx
from backend.app.core.config import settings
from backend.app.core.exceptions import ProviderError
from backend.app.integrations.avatar.base import AvatarProvider, AvatarResult
from backend.app.core.logging import logger

DID_AVATAR_SOURCES = {
    # Male
    "avatar_creator_leo": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=720&q=80",
    "avatar_tech_alex": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=720&q=80",
    "avatar_finance_marcus": "https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?auto=format&fit=crop&w=720&q=80",
    "avatar_podcast_david": "https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=720&q=80",
    # Female
    "avatar_anchor_sarah": "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?auto=format&fit=crop&w=720&q=80",
    "avatar_priya_global": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=720&q=80",
    "avatar_executive_elena": "https://images.unsplash.com/photo-1580489944761-15a19d654956?auto=format&fit=crop&w=720&q=80",
    "avatar_reporter_maya": "https://images.unsplash.com/photo-1567532939604-b6b5b0db2604?auto=format&fit=crop&w=720&q=80",
}

class DIDAvatarProvider(AvatarProvider):
    def __init__(self, api_key: Optional[str] = settings.DID_API_KEY):
        self.api_key = api_key or os.getenv("DID_API_KEY")

    def _get_auth_header(self) -> str:
        if not self.api_key:
            return ""
        if ":" in self.api_key:
            encoded = base64.b64encode(self.api_key.encode("utf-8")).decode("utf-8")
        else:
            encoded = base64.b64encode(f"{self.api_key}:".encode("utf-8")).decode("utf-8")
        return f"Basic {encoded}"

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
            logger.warning("No DID_API_KEY found, falling back to video presenter engine.")
            from backend.app.integrations.avatar.providers.video_presenter import VideoPresenterAvatarProvider
            return await VideoPresenterAvatarProvider().generate_avatar_video(
                script_text, avatar_id, voice_id, duration_seconds, audio_bytes, word_timestamps
            )

        source_url = DID_AVATAR_SOURCES.get(avatar_id, DID_AVATAR_SOURCES["avatar_tech_alex"])
        norm = str(avatar_id).lower()
        d_voice = "en-US-JennyNeural" if any(f in norm for f in ["sarah", "priya", "female"]) else "en-US-GuyNeural"

        logger.info(f"Submitting talking avatar creation to D-ID API for {avatar_id}")

        url = "https://api.d-id.com/talks"
        headers = {
            "Authorization": self._get_auth_header(),
            "Content-Type": "application/json"
        }
        payload = {
            "source_url": source_url,
            "script": {
                "type": "text",
                "input": script_text,
                "provider": {
                    "type": "microsoft",
                    "voice_id": d_voice
                }
            },
            "config": {
                "fluent": True,
                "pad_audio": 0.0
            }
        }

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                res = await client.post(url, json=payload, headers=headers)
                if res.status_code != 201 and res.status_code != 200:
                    raise ProviderError(f"D-ID API error ({res.status_code}): {res.text}")

                data = res.json()
                talk_id = data.get("id")
                if not talk_id:
                    raise ProviderError(f"No talk ID returned by D-ID: {res.text}")

                logger.info(f"D-ID talk job {talk_id} submitted. Polling status...")

                status_url = f"https://api.d-id.com/talks/{talk_id}"
                max_polls = 60
                result_url = None

                for _ in range(max_polls):
                    await asyncio.sleep(4.0)
                    poll_res = await client.get(status_url, headers={"Authorization": self._get_auth_header()})
                    if poll_res.status_code == 200:
                        poll_data = poll_res.json()
                        status = poll_data.get("status")
                        logger.info(f"D-ID talk {talk_id} status: {status}")

                        if status == "done":
                            result_url = poll_data.get("result_url")
                            break
                        elif status == "error":
                            raise ProviderError(f"D-ID talk failed: {poll_data.get('error')}")

                if not result_url:
                    raise ProviderError(f"D-ID video generation timed out for {talk_id}")

                logger.info(f"Downloading D-ID generated talking avatar video from {result_url}...")
                dl_res = await client.get(result_url)
                if dl_res.status_code != 200:
                    raise ProviderError(f"Failed to download D-ID video from {result_url}")

                video_bytes = dl_res.content
                dur = duration_seconds or max(3.0, len(script_text.split()) / 2.5)

                return AvatarResult(
                    video_bytes=video_bytes,
                    duration_seconds=dur,
                    format="mp4",
                    avatar_id=avatar_id,
                    has_alpha=False
                )

        except Exception as e:
            logger.warning(f"D-ID generation failed: {e}. Falling back to video presenter engine.")
            from backend.app.integrations.avatar.providers.video_presenter import VideoPresenterAvatarProvider
            return await VideoPresenterAvatarProvider().generate_avatar_video(
                script_text, avatar_id, voice_id, duration_seconds, audio_bytes, word_timestamps
            )
