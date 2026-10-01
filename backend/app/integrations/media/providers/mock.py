import asyncio
import os
import subprocess
import tempfile
from typing import List
import imageio_ffmpeg
from backend.app.integrations.media.base import MediaProvider, MediaAssetItem
from backend.app.integrations.storage import get_storage_provider

class MockMediaProvider(MediaProvider):
    def __init__(self):
        self.storage = get_storage_provider()

    async def _generate_placeholder_video(self, color_hex: str, duration: float = 5.0) -> str:
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
            tmp_path = tmp.name

        try:
            # 1080x1920 vertical canvas
            cmd = [
                ffmpeg_exe, "-y",
                "-f", "lavfi",
                "-i", f"color=c={color_hex}:s=1080x1920:d={duration}:r=30",
                "-c:v", "libx264",
                "-pix_fmt", "yuv420p",
                "-t", str(duration),
                tmp_path
            ]
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            await proc.communicate()

            with open(tmp_path, "rb") as f:
                data = f.read()

            filename = f"stock_mock_{os.path.basename(tmp_path)}"
            return await self.storage.save_file(data, filename, "video/mp4")
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    async def search_media(
        self,
        query: str,
        asset_type: str = "video",
        count: int = 3
    ) -> List[MediaAssetItem]:
        colors = ["0x1E3A8A", "0x065F46", "0x581C87", "0x831843"]
        items = []
        for i in range(count):
            color = colors[i % len(colors)]
            media_url = await self._generate_placeholder_video(color, 5.0)
            items.append(
                MediaAssetItem(
                    provider="mock_stock",
                    external_id=f"mock_asset_{abs(hash(query)) % 100000}_{i}",
                    asset_type=asset_type,
                    media_url=media_url,
                    thumbnail_url=media_url,
                    license_type="mock_open_license",
                    license_url="https://creativecommons.org/publicdomain/zero/1.0/",
                    attribution_text=f"Mock Stock License for: {query}",
                    duration_seconds=5.0,
                )
            )
        return items
