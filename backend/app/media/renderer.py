import os
import tempfile
import time
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.logging import logger
from backend.app.db.models.render import Render
from backend.app.integrations.storage import get_storage_provider
from backend.app.media.ffmpeg import ffmpeg_engine
from backend.app.media.audio import audio_processor
from backend.app.media.c2pa import c2pa_manager

class VideoRenderer:
    def __init__(self, session: Optional[AsyncSession] = None):
        self.session = session
        self.storage = get_storage_provider()

    async def render_cycle_video(
        self,
        workspace_id: str,
        cycle_id: str,
        title: str,
        scenes: List[Dict[str, Any]],
        voice_audio_bytes: bytes,
        scene_assets: List[Dict[str, Any]],
        avatar_video_bytes: Optional[bytes] = None,
        background_music_bytes: Optional[bytes] = None,
        layout: str = "pip"
    ) -> Dict[str, Any]:
        start_time = time.time()
        temp_files = []

        try:
            # 1. Write voice audio to temp file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f_voice:
                f_voice.write(voice_audio_bytes)
                voice_path = f_voice.name
                temp_files.append(voice_path)

            # 2. Write background music if present
            music_path = None
            if background_music_bytes:
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f_music:
                    f_music.write(background_music_bytes)
                    music_path = f_music.name
                    temp_files.append(music_path)

            # 3. Mix audio (duck music under voice)
            mixed_audio_path = await audio_processor.mix_audio(voice_path, music_path)
            temp_files.append(mixed_audio_path)

            # Detect voiceover duration so speech is never truncated
            audio_duration = 0.0
            try:
                import subprocess
                proc_p = subprocess.run([ffmpeg_engine.ffmpeg_exe, "-i", voice_path], stderr=subprocess.PIPE, text=True)
                for line in proc_p.stderr.split("\n"):
                    if "Duration:" in line:
                        parts = line.split("Duration:")[1].split(",")[0].strip().split(":")
                        audio_duration = float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
                        break
            except Exception:
                pass

            total_duration = max(sum(sc.get("duration_seconds", 4.0) for sc in scenes), audio_duration)
            total_duration = max(3.0, round(total_duration, 1))

            # 4. Extract scene video paths
            scene_paths = []
            for asset in scene_assets:
                storage_url = asset.get("storage_url") or asset.get("media_url")
                if storage_url:
                    try:
                        # If local path or remote URL, get bytes and write temp
                        data = await self.storage.get_file(storage_url)
                        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f_scene:
                            f_scene.write(data)
                            scene_paths.append(f_scene.name)
                            temp_files.append(f_scene.name)
                    except Exception as err:
                        logger.warning(f"Failed to fetch scene asset from {storage_url}: {err}. Skipping asset.")

            # 5. Write avatar video if present
            avatar_path = None
            if avatar_video_bytes:
                with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f_av:
                    f_av.write(avatar_video_bytes)
                    avatar_path = f_av.name
                    temp_files.append(avatar_path)

            # 6. Render final video composition (clean, without captions)
            rendered_mp4_path = await ffmpeg_engine.render_video(
                scene_video_paths=scene_paths,
                audio_path=mixed_audio_path,
                subtitle_path=None,
                avatar_path=avatar_path,
                duration=total_duration,
                layout=layout
            )
            temp_files.append(rendered_mp4_path)

            # 7. Extract thumbnail
            thumb_path = await ffmpeg_engine.extract_thumbnail(rendered_mp4_path, timestamp=1.0)
            temp_files.append(thumb_path)

            # 8. Upload artifacts to object storage
            with open(rendered_mp4_path, "rb") as f:
                video_bytes = f.read()
            video_url = await self.storage.save_file(video_bytes, f"renders/{cycle_id}/final_video.mp4", "video/mp4")

            with open(thumb_path, "rb") as f:
                thumb_bytes = f.read()
            thumbnail_url = await self.storage.save_file(thumb_bytes, f"renders/{cycle_id}/thumbnail.jpg", "image/jpeg")

            captions_url = None

            # 9. Generate C2PA authenticity manifest
            manifest = c2pa_manager.generate_manifest(title=title)
            render_duration = round(time.time() - start_time, 2)

            render_info = {
                "cycle_id": cycle_id,
                "video_url": video_url,
                "thumbnail_url": thumbnail_url,
                "captions_url": captions_url,
                "resolution": "1080x1920",
                "aspect_ratio": "9:16",
                "duration_seconds": total_duration,
                "file_size_bytes": len(video_bytes),
                "render_time_seconds": render_duration,
                "c2pa_manifest_id": manifest["manifest_id"]
            }

            # 11. Save record in database if session available
            if self.session:
                render_record = Render(
                    workspace_id=workspace_id,
                    cycle_id=cycle_id,
                    video_url=video_url,
                    thumbnail_url=thumbnail_url,
                    captions_url=captions_url,
                    resolution="1080x1920",
                    aspect_ratio="9:16",
                    duration_seconds=total_duration,
                    file_size_bytes=len(video_bytes),
                    render_time_seconds=render_duration,
                    c2pa_manifest_id=manifest["manifest_id"]
                )
                self.session.add(render_record)
                await self.session.flush()

            logger.info(f"Video render completed in {render_duration}s for cycle {cycle_id}")
            return render_info

        finally:
            for p in temp_files:
                if os.path.exists(p):
                    try:
                        os.unlink(p)
                    except Exception:
                        pass
