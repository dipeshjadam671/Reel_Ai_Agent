import asyncio
import os
import subprocess
import tempfile
from typing import List, Optional
import imageio_ffmpeg
from backend.app.core.exceptions import AppException
from backend.app.core.constants import ErrorCode
from backend.app.core.logging import logger

class FFmpegEngine:
    def __init__(self):
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    async def render_video(
        self,
        scene_video_paths: List[str],
        audio_path: str,
        subtitle_path: Optional[str] = None,
        avatar_path: Optional[str] = None,
        output_path: Optional[str] = None,
        duration: float = 15.0,
        layout: str = "pip"
    ) -> str:
        if not output_path:
            with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp:
                output_path = tmp.name

        # Create concat demuxer file if multiple scenes
        concat_file = None
        has_scenes = len(scene_video_paths) > 0
        if len(scene_video_paths) > 1:
            with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as cf:
                for p in scene_video_paths:
                    cf.write(f"file '{p}'\n")
                concat_file = cf.name
            input_v = ["-f", "concat", "-safe", "0", "-i", concat_file]
        elif len(scene_video_paths) == 1:
            input_v = ["-i", scene_video_paths[0]]
        else:
            # Fallback test canvas
            input_v = ["-f", "lavfi", "-i", f"color=c=0x0f172a:s=1080x1920:d={duration}:r=30"]

        cmd = [self.ffmpeg_exe, "-y"]
        cmd.extend(input_v)
        cmd.extend(["-i", audio_path])

        filter_chain = []
        video_map = "0:v"

        has_avatar = avatar_path and os.path.exists(avatar_path)
        if has_avatar:
            cmd.extend(["-i", avatar_path])

        norm_layout = str(layout).lower()

        if has_avatar:
            if norm_layout == "background" or not has_scenes:
                # Presenter Centered: Avatar is the primary full-screen visual
                filter_chain.append("[2:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[base]")
                video_map = "[base]"
            elif norm_layout == "split":
                # Split Screen: Top is B-Roll, Bottom is Presenter
                filter_chain.append("[0:v]scale=1080:960:force_original_aspect_ratio=increase,crop=1080:960[top]")
                filter_chain.append("[2:v]scale=1080:960:force_original_aspect_ratio=increase,crop=1080:960[bottom]")
                filter_chain.append("[top][bottom]vstack[base]")
                video_map = "[base]"
            else:
                # Picture-in-Picture: Avatar in lower right corner
                filter_chain.append("[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[bg]")
                filter_chain.append("[2:v]scale=380:660,format=yuva420p[av]")
                filter_chain.append("[bg][av]overlay=660:1180[base]")
                video_map = "[base]"
        else:
            filter_chain.append("[0:v]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920[base]")
            video_map = "[base]"


        if filter_chain:
            cmd.extend(["-filter_complex", ";".join(filter_chain)])
            cmd.extend(["-map", video_map])
        else:
            cmd.extend(["-map", "0:v"])

        cmd.extend([
            "-map", "1:a",
            "-c:v", "libx264",
            "-preset", "ultrafast",
            "-pix_fmt", "yuv420p",
            "-c:a", "aac",
            "-b:a", "192k",
            "-shortest",
            "-t", str(duration),
            output_path
        ])

        try:
            logger.info("Executing FFmpeg composition render...")
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE
            )
            _, stderr = await proc.communicate()
            if proc.returncode != 0:
                logger.error(f"FFmpeg render error (return code {proc.returncode}): {stderr.decode(errors='ignore')}")
                raise AppException(
                    code=ErrorCode.RENDER_FAILED,
                    message="Video composition failed during FFmpeg encoding"
                )
            return output_path
        finally:
            if concat_file and os.path.exists(concat_file):
                os.unlink(concat_file)

    async def extract_thumbnail(self, video_path: str, output_path: Optional[str] = None, timestamp: float = 1.0) -> str:
        if not output_path:
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
                output_path = tmp.name

        cmd = [
            self.ffmpeg_exe, "-y",
            "-ss", str(timestamp),
            "-i", video_path,
            "-vframes", "1",
            "-q:v", "2",
            output_path
        ]
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        await proc.communicate()
        return output_path

ffmpeg_engine = FFmpegEngine()
