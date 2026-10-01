import asyncio
import os
import subprocess
import tempfile
from typing import Any, Dict, List, Optional, Tuple
import imageio_ffmpeg
from PIL import Image, ImageDraw

from backend.app.integrations.avatar.base import AvatarProvider, AvatarResult
from backend.app.core.logging import logger

VIDEO_PRESENTER_CONFIGS = {
    # --- MALE PRESENTERS ---
    "avatar_creator_leo": {
        "video": "leo_presenter.mp4",
        "crop": "crop=405:720:437:0,scale=720:1280",
        "name": "LEO",
        "gender": "male",
        "title": "CREATIVE DIRECTOR & HOST",
        "badge": "AI AUTONOMOUS PRESENTER",
        "accent": (16, 185, 129, 230),  # Emerald
        "accent_hex": "#10b981",
        "border_color": (16, 185, 129, 230),
        "default_voice": "fable",
        "description": "Charismatic studio director with executive presence, suited for high-impact brand launches and creative narratives.",
    },
    "avatar_tech_alex": {
        "video": "alex_presenter.mp4",
        "crop": "crop=607:1080:420:0,scale=720:1280",
        "name": "ALEX",
        "gender": "male",
        "title": "AI & TECH SPECIALIST",
        "badge": "DIGITAL MEDIA CREATOR",
        "accent": (99, 102, 241, 230),  # Indigo
        "accent_hex": "#6366f1",
        "border_color": (99, 102, 241, 230),
        "default_voice": "onyx",
        "description": "Modern tech builder in studio headphones, perfect for coding tutorials, AI workflows, and software deep dives.",
    },
    "avatar_finance_marcus": {
        "video": "marcus_presenter.mp4",
        "crop": "crop=405:720:540:0,scale=720:1280",
        "name": "MARCUS",
        "gender": "male",
        "title": "FINANCIAL & TECH ANALYST",
        "badge": "STUDIO TECH PODCASTER",
        "accent": (59, 130, 246, 230),  # Blue
        "accent_hex": "#3b82f6",
        "border_color": (59, 130, 246, 230),
        "default_voice": "echo",
        "description": "Studio podcaster with gold condenser mic and cinematic lighting, ideal for macro markets, crypto, and VC analysis.",
    },
    "avatar_podcast_david": {
        "video": "david_presenter.mp4",
        "crop": "scale=720:1280",
        "name": "DAVID",
        "gender": "male",
        "title": "INVESTIGATIVE JOURNALIST",
        "badge": "BROADCAST RADIO HOST",
        "accent": (139, 92, 246, 230),  # Violet
        "accent_hex": "#8b5cf6",
        "border_color": (139, 92, 246, 230),
        "default_voice": "onyx",
        "description": "Warm and authoritative broadcast radio host with studio headphones, excellent for journalism, news, and investigative series.",
    },

    # --- FEMALE PRESENTERS ---
    "avatar_anchor_sarah": {
        "video": "sarah_presenter.mp4",
        "crop": "crop=607:1080:596:0,scale=720:1280",
        "name": "SARAH",
        "gender": "female",
        "title": "CHIEF CORRESPONDENT",
        "badge": "STUDIO BROADCAST ANCHOR",
        "accent": (245, 158, 11, 230),  # Amber
        "accent_hex": "#f59e0b",
        "border_color": (245, 158, 11, 230),
        "default_voice": "nova",
        "description": "Chief broadcast journalist with engaging delivery, perfect for breaking tech news, enterprise reporting, and executive briefs.",
    },
    "avatar_priya_global": {
        "video": "priya_presenter.mp4",
        "crop": "scale=720:1280",
        "name": "PRIYA",
        "gender": "female",
        "title": "GLOBAL MEDIA HOST",
        "badge": "PODCAST & BROADCAST HOST",
        "accent": (6, 182, 212, 230),  # Cyan
        "accent_hex": "#06b6d4",
        "border_color": (6, 182, 212, 230),
        "default_voice": "shimmer",
        "description": "International broadcast host at studio sound console, great for global culture, multilingual content, and creator economy.",
    },
    "avatar_executive_elena": {
        "video": "elena_presenter.mp4",
        "crop": "crop=405:720:450:0,scale=720:1280",
        "name": "ELENA",
        "gender": "female",
        "title": "EXECUTIVE STRATEGIST",
        "badge": "TECH KEYNOTE PRESENTER",
        "accent": (244, 63, 94, 230),  # Rose
        "accent_hex": "#f43f5e",
        "border_color": (244, 63, 94, 230),
        "default_voice": "alloy",
        "description": "Polished Silicon Valley strategist in tailored blazer, ideal for product announcements, executive thought leadership, and masterclasses.",
    },
    "avatar_reporter_maya": {
        "video": "maya_presenter.mp4",
        "crop": "scale=720:1280",
        "name": "MAYA",
        "gender": "female",
        "title": "DIGITAL CULTURE & TRENDS",
        "badge": "STUDIO BROADCAST HOST",
        "accent": (217, 70, 239, 230),  # Fuchsia
        "accent_hex": "#d946ef",
        "border_color": (217, 70, 239, 230),
        "default_voice": "shimmer",
        "description": "Energetic studio audio broadcaster, ideal for pop culture trends, social media analysis, and creator interviews.",
    },
}

def get_available_personas() -> List[Dict[str, Any]]:
    """Returns metadata for all available video presenter personas."""
    result = []
    for key, cfg in VIDEO_PRESENTER_CONFIGS.items():
        result.append({
            "id": key,
            "name": cfg["name"],
            "gender": cfg["gender"],
            "title": cfg["title"],
            "badge": cfg["badge"],
            "accent_hex": cfg.get("accent_hex", "#10b981"),
            "default_voice": cfg.get("default_voice", "onyx"),
            "description": cfg.get("description", ""),
            "thumbnail_url": f"/avatars/{cfg['name'].lower()}.jpg",
        })
    return result

class VideoPresenterAvatarProvider(AvatarProvider):
    """
    True High-Definition Speaking Video Presenter Engine.
    Uses real studio video footage of speaking presenters, loops seamlessly to match
    exact narration speech duration, and composites high-definition broadcast overlays.
    """

    def __init__(self):
        self.videos_dir = os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "assets", "avatars", "videos"
        )
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    def _resolve_persona(self, avatar_id: str) -> Tuple[str, Dict[str, Any]]:
        norm = str(avatar_id).lower()
        if "marcus" in norm or "finance" in norm:
            key = "avatar_finance_marcus"
        elif "david" in norm or "podcast" in norm or "investigative" in norm:
            key = "avatar_podcast_david"
        elif "leo" in norm or "creator" in norm:
            key = "avatar_creator_leo"
        elif "sarah" in norm or "anchor" in norm:
            key = "avatar_anchor_sarah"
        elif "elena" in norm or "executive" in norm or "keynote" in norm:
            key = "avatar_executive_elena"
        elif "maya" in norm or "reporter" in norm or "culture" in norm:
            key = "avatar_reporter_maya"
        elif "priya" in norm or "global" in norm:
            key = "avatar_priya_global"
        else:
            key = "avatar_tech_alex"
        return key, VIDEO_PRESENTER_CONFIGS[key]

    def _create_broadcast_overlay(self, cfg: Dict[str, Any], output_png: str) -> None:
        """
        Creates a crisp 720x1280 broadcast graphic overlay with LIVE badge,
        persona lower-third, and sleek rounded accent border.
        """
        w, h = 720, 1280
        overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(overlay)

        accent = cfg["accent"]

        # Outer rounded broadcast border
        draw.rounded_rectangle([12, 12, w - 12, h - 12], radius=28, outline=accent, width=6)

        # Top-left LIVE status badge
        draw.rounded_rectangle(
            [32, 32, 170, 84],
            radius=14,
            fill=(15, 23, 42, 220),
            outline=(239, 68, 68, 240),
            width=2,
        )
        draw.ellipse([46, 48, 64, 66], fill=(239, 68, 68, 255))
        draw.text((76, 42), "LIVE", fill=(255, 255, 255, 255), font_size=24)

        # Bottom Presenter Lower-Third card
        draw.rounded_rectangle(
            [32, 1110, w - 32, 1230],
            radius=20,
            fill=(15, 23, 42, 230),
            outline=accent,
            width=3,
        )
        draw.text(
            (54, 1126),
            f"{cfg['name']} | {cfg['title']}",
            fill=(255, 255, 255, 255),
            font_size=24,
        )
        draw.text(
            (54, 1168),
            f"{cfg['badge']} | AI SYNCHRONIZED",
            fill=(148, 163, 184, 255),
            font_size=16,
        )

        overlay.save(output_png)

    async def generate_avatar_video(
        self,
        script_text: str,
        avatar_id: str = "avatar_alex",
        voice_id: Optional[str] = None,
        duration_seconds: Optional[float] = None,
        audio_bytes: Optional[bytes] = None,
        word_timestamps: Optional[List[Dict[str, Any]]] = None,
    ) -> AvatarResult:
        persona_key, cfg = self._resolve_persona(avatar_id)
        video_filename = cfg["video"]
        video_path = os.path.join(self.videos_dir, video_filename)

        if not os.path.exists(video_path):
            logger.warning(
                f"Presenter video file not found at {video_path}, checking legacy assets..."
            )
            # Fall back to lipsync engine if video file is missing
            from backend.app.integrations.avatar.providers.lipsync import LipSyncAvatarProvider
            return await LipSyncAvatarProvider().generate_avatar_video(
                script_text, avatar_id, voice_id, duration_seconds, audio_bytes, word_timestamps
            )

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f_audio, \
             tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f_badge, \
             tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as f_out:
            audio_path = f_audio.name
            badge_png = f_badge.name
            out_mp4 = f_out.name

        try:
            # Measure speech duration from audio if available
            detected_dur = 0.0
            has_audio = False
            if audio_bytes and len(audio_bytes) > 0:
                with open(audio_path, "wb") as f:
                    f.write(audio_bytes)
                has_audio = True

                try:
                    proc_probe = subprocess.run(
                        [self.ffmpeg_exe, "-i", audio_path],
                        stderr=subprocess.PIPE,
                        stdout=subprocess.DEVNULL,
                        text=True,
                    )
                    for line in proc_probe.stderr.split("\n"):
                        if "Duration:" in line:
                            parts = line.split("Duration:")[1].split(",")[0].strip().split(":")
                            detected_dur = float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
                            break
                except Exception as e:
                    logger.warning(f"Failed to probe audio duration: {e}")

            if detected_dur > 0:
                dur = detected_dur
            elif duration_seconds:
                dur = duration_seconds
            else:
                dur = max(4.0, len(script_text.split()) / 2.5)

            dur = max(2.5, round(dur, 2))

            # Build graphic overlay badge
            self._create_broadcast_overlay(cfg, badge_png)

            # Assemble video pipeline with FFmpeg
            filter_complex = f"[0:v]{cfg['crop']}[base];[base][1:v]overlay=0:0[vout]"
            cmd = [
                self.ffmpeg_exe, "-y",
                "-stream_loop", "-1",
                "-i", video_path,
                "-i", badge_png,
            ]

            if has_audio:
                cmd.extend([
                    "-i", audio_path,
                    "-filter_complex", filter_complex,
                    "-map", "[vout]",
                    "-map", "2:a",
                    "-c:v", "libx264",
                    "-preset", "veryfast",
                    "-pix_fmt", "yuv420p",
                    "-c:a", "aac",
                    "-b:a", "192k",
                    "-shortest",
                    "-t", str(dur),
                    out_mp4,
                ])
            else:
                cmd.extend([
                    "-filter_complex", filter_complex,
                    "-map", "[vout]",
                    "-c:v", "libx264",
                    "-preset", "veryfast",
                    "-pix_fmt", "yuv420p",
                    "-t", str(dur),
                    out_mp4,
                ])

            logger.info(
                f"Rendering studio video presenter for {cfg['name']} ({dur:.2f}s, source: {video_filename})"
            )

            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
            )
            _, stderr = await proc.communicate()

            if proc.returncode != 0:
                logger.error(f"FFmpeg presenter render failed: {stderr.decode(errors='ignore')}")
                raise RuntimeError("Failed to render presenter video")

            with open(out_mp4, "rb") as f:
                video_data = f.read()

            logger.info(
                f"Generated studio video presenter MP4 for {cfg['name']}: {dur:.2f}s, {len(video_data)} bytes"
            )

            return AvatarResult(
                video_bytes=video_data,
                duration_seconds=dur,
                format="mp4",
                avatar_id=persona_key,
                has_alpha=False,
            )

        finally:
            for p in [audio_path, badge_png, out_mp4]:
                if os.path.exists(p):
                    try:
                        os.unlink(p)
                    except Exception:
                        pass
