import asyncio
import os
import subprocess
import tempfile
from typing import Optional
import imageio_ffmpeg
from backend.app.core.logging import logger

class AudioProcessor:
    def __init__(self):
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    async def mix_audio(
        self,
        voiceover_path: str,
        background_music_path: Optional[str] = None,
        output_path: Optional[str] = None,
        music_volume: float = 0.15
    ) -> str:
        if not output_path:
            with tempfile.NamedTemporaryFile(suffix=".aac", delete=False) as tmp:
                output_path = tmp.name

        if not background_music_path or not os.path.exists(background_music_path):
            # Normalize voiceover directly
            cmd = [
                self.ffmpeg_exe, "-y",
                "-i", voiceover_path,
                "-af", "loudnorm=I=-16:LRA=11:TP=-1.5",
                "-c:a", "aac",
                "-b:a", "192k",
                output_path
            ]
        else:
            # Sidechain ducking: voiceover ducks background music
            filter_complex = f"[1:a]volume={music_volume}[music];[0:a][music]amix=inputs=2:duration=first:dropout_transition=2[outa]"
            cmd = [
                self.ffmpeg_exe, "-y",
                "-i", voiceover_path,
                "-i", background_music_path,
                "-filter_complex", filter_complex,
                "-map", "[outa]",
                "-c:a", "aac",
                "-b:a", "192k",
                output_path
            ]

        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        await proc.communicate()
        return output_path

audio_processor = AudioProcessor()
