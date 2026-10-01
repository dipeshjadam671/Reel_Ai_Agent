import asyncio
import io
import math
import os
import re
import subprocess
import tempfile
import wave
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import imageio_ffmpeg
from backend.app.integrations.avatar.base import AvatarProvider, AvatarResult
from backend.app.core.logging import logger

PERSONA_CONFIGS = {
    "avatar_creator_leo": {
        "name": "LEO",
        "title": "CREATIVE DIRECTOR & HOST",
        "neutral": "leo_neutral.jpg",
        "dental": "leo_dental.jpg",
        "vowel": "leo_vowel.jpg",
        "round": "leo_round.jpg",
        "spread": "leo_spread.jpg",
        "accent_color": (16, 185, 129),  # Emerald
        "badge_border": (5, 150, 105),
    },
    "avatar_anchor_sarah": {
        "name": "SARAH",
        "title": "CHIEF CORRESPONDENT",
        "neutral": "sarah_neutral.jpg",
        "dental": "sarah_neutral.jpg",
        "vowel": "sarah_vowel.jpg",
        "round": "sarah_vowel.jpg",
        "spread": "sarah_vowel.jpg",
        "accent_color": (59, 130, 246),  # Blue
        "badge_border": (37, 99, 235),
    },
    "avatar_tech_alex": {
        "name": "ALEX",
        "title": "AI & TECH SPECIALIST",
        "neutral": "alex_neutral.jpg",
        "dental": "alex_dental.jpg",
        "vowel": "alex_vowel.jpg",
        "round": "alex_vowel.jpg",
        "spread": "alex_dental.jpg",
        "accent_color": (99, 102, 241),  # Indigo
        "badge_border": (79, 70, 229),
    },
    "avatar_priya_global": {
        "name": "PRIYA",
        "title": "GLOBAL MEDIA HOST",
        "neutral": "priya_neutral.jpg",
        "dental": "priya_speaking_mid.jpg",
        "vowel": "priya_speaking_open.jpg",
        "round": "priya_speaking_open.jpg",
        "spread": "priya_speaking_mid.jpg",
        "accent_color": (20, 184, 166),  # Teal
        "badge_border": (13, 148, 136),
    },
}

ROUND_WORDS = {
    "to", "do", "you", "who", "through", "true", "two", "look", "good", "book", "would",
    "could", "should", "no", "so", "go", "flow", "know", "show", "world", "all", "more",
    "your", "four", "for", "or", "how", "now", "out", "about", "down", "round", "voice",
    "video", "audio", "one", "won", "worth", "work", "word", "over", "open", "old", "only"
}

SPREAD_WORDS = {
    "see", "key", "me", "we", "he", "she", "be", "say", "day", "way", "make", "take",
    "great", "late", "face", "place", "state", "create", "these", "read", "lead", "need",
    "deep", "keep", "feel", "deal", "real", "clear", "here", "team", "people", "easy"
}

BILABIAL_WORDS = {
    "my", "me", "more", "make", "much", "many", "most", "may", "be", "by", "but", "best",
    "better", "business", "power", "people", "point", "part", "problem", "plan", "play"
}

class LipSyncAvatarProvider(AvatarProvider):
    def __init__(self):
        self.assets_dir = os.path.join(
            os.path.dirname(__file__), "..", "..", "..", "assets", "avatars"
        )
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    def _resolve_persona(self, avatar_id: str) -> Tuple[str, Dict[str, Any]]:
        norm = str(avatar_id).lower()
        if "leo" in norm or "creator" in norm:
            key = "avatar_creator_leo"
        elif "sarah" in norm or "anchor" in norm or "news" in norm:
            key = "avatar_anchor_sarah"
        elif "priya" in norm or "female" in norm or "global" in norm:
            key = "avatar_priya_global"
        else:
            key = "avatar_tech_alex"
        return key, PERSONA_CONFIGS[key]

    def _load_persona_images(self, cfg: Dict[str, Any]) -> Dict[str, Image.Image]:
        states = {}
        for state_key in ["neutral", "dental", "vowel", "round", "spread"]:
            filename = cfg.get(state_key)
            filepath = os.path.join(self.assets_dir, filename) if filename else None
            if filepath and os.path.exists(filepath):
                try:
                    orig = Image.open(filepath).convert("RGB")
                    w, h = orig.size
                    if w == h:
                        scaled = orig.resize((960, 960), Image.Resampling.LANCZOS)
                        crop_x = (960 - 540) // 2
                        cropped = scaled.crop((crop_x, 0, crop_x + 540, 960))
                    else:
                        cropped = orig.resize((540, 960), Image.Resampling.LANCZOS)
                    states[state_key] = cropped
                except Exception as e:
                    logger.warning(f"Failed to load {filepath}: {e}")
            
        # Ensure fallbacks if specific viseme is missing
        neutral = states.get("neutral")
        if not neutral:
            neutral = Image.new("RGB", (540, 960), (30, 41, 59))
            states["neutral"] = neutral

        states.setdefault("dental", states.get("neutral"))
        states.setdefault("vowel", states.get("dental"))
        states.setdefault("round", states.get("vowel"))
        states.setdefault("spread", states.get("dental"))
        return states

    def _extract_pcm_and_envelope(
        self, audio_bytes: Optional[bytes], fps: int = 24
    ) -> Tuple[Optional[str], np.ndarray, float, float]:
        """
        Converts audio_bytes to 24000Hz 16-bit mono WAV, computes per-frame RMS speech envelope.
        Returns: (wav_filepath, rms_envelope_array, total_duration, peak_rms)
        """
        if not audio_bytes:
            return None, np.array([]), 0.0, 0.0

        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f_in, \
             tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f_out:
            f_in.write(audio_bytes)
            f_in.flush()
            in_path = f_in.name
            out_path = f_out.name

        try:
            # Normalize to 24000Hz 16-bit mono WAV
            cmd = [
                self.ffmpeg_exe, "-y",
                "-i", in_path,
                "-ac", "1",
                "-ar", "24000",
                out_path
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

            with wave.open(out_path, "rb") as wf:
                framerate = wf.getframerate()
                n_frames = wf.getnframes()
                raw_data = wf.readframes(n_frames)

            samples = np.frombuffer(raw_data, dtype=np.int16).astype(np.float32)
            duration = len(samples) / float(framerate)
            samples_per_frame = int(framerate / fps)
            num_frames = int(math.ceil(duration * fps))

            rms_list = []
            for f in range(num_frames):
                start_idx = f * samples_per_frame
                end_idx = min(len(samples), (f + 1) * samples_per_frame)
                if start_idx < len(samples) and end_idx > start_idx:
                    chunk = samples[start_idx:end_idx]
                    rms = float(np.sqrt(np.mean(chunk**2)))
                else:
                    rms = 0.0
                rms_list.append(rms)

            rms_arr = np.array(rms_list, dtype=np.float32)
            peak_rms = float(rms_arr.max()) if len(rms_arr) > 0 else 0.0
            return out_path, rms_arr, duration, peak_rms
        finally:
            if os.path.exists(in_path):
                os.unlink(in_path)

    def _build_word_schedule(
        self, script_text: str, total_duration: float, word_timestamps: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """
        Returns a list of word dictionaries with:
        [{'word': 'Hello', 'start': 0.0, 'end': 0.45, 'clean': 'hello', 'type': 'vowel'}, ...]
        """
        words = script_text.split()
        if not words:
            return []

        if word_timestamps and len(word_timestamps) == len(words):
            schedule = []
            for item in word_timestamps:
                w = item.get("word", "")
                clean = re.sub(r"[^a-zA-Z]", "", w).lower()
                schedule.append({
                    "word": w,
                    "start": float(item.get("start", 0.0)),
                    "end": float(item.get("end", 0.0)),
                    "clean": clean
                })
            return schedule

        # Distribute words with realistic pauses at punctuation
        schedule = []
        base_word_time = max(0.22, (total_duration * 0.85) / max(1, len(words)))
        curr_time = 0.15  # Small initial silence

        for idx, w in enumerate(words):
            clean = re.sub(r"[^a-zA-Z]", "", w).lower()
            # Longer words take more time
            w_dur = base_word_time * (1.0 + 0.06 * max(0, len(clean) - 4))
            w_start = curr_time
            w_end = min(total_duration, w_start + w_dur)
            schedule.append({
                "word": w,
                "start": w_start,
                "end": w_end,
                "clean": clean
            })
            curr_time = w_end
            # Extra pause on punctuation
            if w.endswith((".", "!", "?")):
                curr_time += 0.45
            elif w.endswith((",", ";", ":", "—")):
                curr_time += 0.25
            else:
                curr_time += 0.04

        return schedule

    def _determine_frame_viseme(
        self,
        t: float,
        rms: float,
        silence_threshold: float,
        peak_rms: float,
        word_schedule: List[Dict[str, Any]],
        available_states: Dict[str, Image.Image]
    ) -> Tuple[str, float]:
        """
        Determines the exact viseme target ('neutral', 'dental', 'vowel', 'round', 'spread')
        and speech intensity factor (0.0 to 1.0) for time t.
        """
        # Strict silence check: mouth is closed if energy is below speech threshold
        if rms < silence_threshold or peak_rms <= 0:
            return "neutral", 0.0

        # Find if a word is currently active
        active_word = None
        for item in word_schedule:
            if item["start"] <= t <= item["end"]:
                active_word = item
                break

        if not active_word:
            # During pauses between words: strictly neutral
            return "neutral", 0.0

        # Compute speech intensity
        intensity = min(1.0, max(0.0, (rms - silence_threshold) / (peak_rms - silence_threshold + 1e-5)))

        clean = active_word["clean"]
        w_dur = max(0.05, active_word["end"] - active_word["start"])
        progress = (t - active_word["start"]) / w_dur

        # Syllable onset (consonant or initial closure)
        if progress < 0.18:
            if clean and clean[0] in "mbp":
                return "neutral", intensity * 0.2  # Bilabial closed lips
            return "dental", intensity

        # Syllable coda (ending sound)
        if progress > 0.82:
            if clean and clean[-1] in "mbp":
                return "neutral", intensity * 0.2
            return "dental", intensity

        # Syllable Nucleus (vowel core)
        if clean in ROUND_WORDS or any(sub in clean for sub in ["oo", "ou", "ow", "who", "two"]):
            if "round" in available_states:
                return "round", intensity
            return "vowel", intensity

        if clean in SPREAD_WORDS or any(sub in clean for sub in ["ee", "ea", "ey", "ay"]):
            if "spread" in available_states:
                return "spread", intensity
            return "dental", intensity

        # General open vowels vs dental consonants
        if intensity > 0.35 and any(v in clean for v in "aeiou"):
            return "vowel", intensity
        else:
            return "dental", intensity

    async def generate_avatar_video(
        self,
        script_text: str,
        avatar_id: str = "avatar_alex",
        voice_id: Optional[str] = None,
        duration_seconds: Optional[float] = None,
        audio_bytes: Optional[bytes] = None,
        word_timestamps: Optional[List[Dict[str, Any]]] = None
    ) -> AvatarResult:
        persona_key, cfg = self._resolve_persona(avatar_id)
        states = self._load_persona_images(cfg)

        fps = 24
        wav_path, rms_env, detected_dur, peak_rms = self._extract_pcm_and_envelope(audio_bytes, fps=fps)

        if detected_dur > 0:
            dur = detected_dur
        elif duration_seconds:
            dur = duration_seconds
        else:
            dur = max(3.0, len(script_text.split()) / 2.5)

        total_frames = max(1, int(math.ceil(dur * fps)))

        # Silence threshold: 8% of peak speech RMS, or baseline 250
        silence_threshold = max(250.0, peak_rms * 0.08)

        # Word timing schedule
        word_schedule = self._build_word_schedule(script_text, dur, word_timestamps)

        logger.info(
            f"Generating lip-synced avatar video for {cfg['name']} ({dur:.2f}s, {total_frames} frames, "
            f"peak RMS: {peak_rms:.1f}, silence threshold: {silence_threshold:.1f})"
        )

        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp_out:
            tmp_mp4 = tmp_out.name

        try:
            with tempfile.TemporaryDirectory() as tmp_dir:
                # Pre-calculate viseme sequence with temporal smoothing
                viseme_seq = []
                for f in range(total_frames):
                    t = f / float(fps)
                    rms = float(rms_env[f]) if f < len(rms_env) else 0.0
                    viseme, intensity = self._determine_frame_viseme(
                        t=t,
                        rms=rms,
                        silence_threshold=silence_threshold,
                        peak_rms=peak_rms,
                        word_schedule=word_schedule,
                        available_states=states
                    )
                    viseme_seq.append((viseme, intensity, rms))

                # Render each frame
                for f in range(total_frames):
                    t = f / float(fps)
                    viseme, intensity, rms = viseme_seq[f]

                    # Smooth transition: if switching viseme from previous frame, take gentle blend
                    current_img = states.get(viseme, states["neutral"])
                    if f > 0 and viseme_seq[f - 1][0] != viseme:
                        prev_viseme = viseme_seq[f - 1][0]
                        prev_img = states.get(prev_viseme, states["neutral"])
                        face = Image.blend(prev_img, current_img, 0.65)
                    else:
                        face = current_img

                    # Canvas (9:16 vertical video: 540x960)
                    canvas = Image.new("RGB", (540, 960), (15, 23, 42))

                    # Subtle organic breathing motion (gentle micro-float)
                    offset_y = int(2.5 * math.sin(t * 2.0))
                    offset_x = int(1.2 * math.cos(t * 1.5))
                    canvas.paste(face, (offset_x, offset_y))

                    draw = ImageDraw.Draw(canvas)

                    # Sleek rounded border with persona accent color
                    accent_col = cfg["accent_color"]
                    draw.rounded_rectangle([8, 8, 532, 952], radius=24, outline=accent_col, width=5)

                    # Top-left LIVE broadcast badge
                    live_pulse = 0.5 + 0.5 * math.sin(t * 4.0)
                    red_val = int(200 + 55 * live_pulse)
                    draw.rounded_rectangle([25, 25, 140, 68], radius=12, fill=(15, 23, 42), outline=(239, 68, 68), width=2)
                    draw.ellipse([38, 38, 52, 52], fill=(red_val, 30, 30))
                    draw.text((62, 34), "LIVE", fill=(255, 255, 255), font_size=20)

                    # Bottom Presenter Name & Role Lower-Third
                    draw.rounded_rectangle([25, 830, 515, 925], radius=16, fill=(15, 23, 42), outline=accent_col, width=2)
                    draw.text((45, 842), f"{cfg['name']} | {cfg['title']}", fill=(255, 255, 255), font_size=22)
                    draw.text((45, 876), "AI SYNCHRONIZED PRESENTER", fill=(148, 163, 184), font_size=15)

                    # Real-time reactive audio equalizer wave bars (driven by actual frame RMS)
                    for b in range(7):
                        freq_mult = 1.0 + b * 0.25
                        bar_react = intensity * math.sin(t * 18.0 * freq_mult + b)
                        bar_h = max(4, int(22 * intensity * (0.6 + 0.4 * abs(bar_react))))
                        bx = 405 + b * 13
                        draw.rounded_rectangle([bx, 908 - bar_h, bx + 7, 908], radius=3, fill=accent_col)

                    frame_file = os.path.join(tmp_dir, f"frame_{f:04d}.jpg")
                    canvas.save(frame_file, quality=92)

                # Assemble with FFmpeg, multiplexing audio if available
                cmd = [
                    self.ffmpeg_exe, "-y",
                    "-framerate", str(fps),
                    "-i", os.path.join(tmp_dir, "frame_%04d.jpg")
                ]

                if wav_path and os.path.exists(wav_path):
                    cmd.extend([
                        "-i", wav_path,
                        "-c:v", "libx264",
                        "-preset", "ultrafast",
                        "-pix_fmt", "yuv420p",
                        "-c:a", "aac",
                        "-b:a", "192k",
                        "-shortest",
                        "-t", str(dur),
                        tmp_mp4
                    ])
                else:
                    cmd.extend([
                        "-c:v", "libx264",
                        "-preset", "ultrafast",
                        "-pix_fmt", "yuv420p",
                        "-t", str(dur),
                        tmp_mp4
                    ])

                proc = await asyncio.create_subprocess_exec(
                    *cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                await proc.communicate()

            with open(tmp_mp4, "rb") as f:
                video_data = f.read()

            logger.info(
                f"Generated synchronized avatar MP4: {dur:.2f}s, {len(video_data)} bytes for {cfg['name']}"
            )
            return AvatarResult(
                video_bytes=video_data,
                duration_seconds=dur,
                format="mp4",
                avatar_id=persona_key,
                has_alpha=False
            )
        finally:
            if wav_path and os.path.exists(wav_path):
                os.unlink(wav_path)
            if os.path.exists(tmp_mp4):
                os.unlink(tmp_mp4)
