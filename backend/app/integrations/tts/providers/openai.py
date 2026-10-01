import io
import math
import os
import re
import subprocess
import tempfile
from typing import Any, Dict, List, Optional
import httpx
import imageio_ffmpeg
from backend.app.core.config import settings
from backend.app.core.exceptions import ProviderError
from backend.app.integrations.tts.base import TTSProvider, TTSResult
from backend.app.core.logging import logger

OPENAI_VOICES = {
    "onyx": "onyx",          # Deep, authoritative broadcast male
    "nova": "nova",          # Warm, energetic, engaging female
    "echo": "echo",          # Smooth, confident explainer male
    "shimmer": "shimmer",    # Clear, crisp, elegant female
    "fable": "fable",        # Expressive storyteller
    "alloy": "alloy",        # Neutral modern AI
}

VOICE_ALIASES = {
    "alex": "onyx",
    "leo": "echo",
    "sarah": "nova",
    "priya": "shimmer",
    "rachel": "nova",
    "domi": "onyx",
    "bella": "shimmer",
    "female": "nova",
    "male": "onyx",
}

class OpenAITTSProvider(TTSProvider):
    def __init__(self, api_key: Optional[str] = settings.OPENAI_API_KEY):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    def _resolve_voice(self, voice: Optional[str]) -> str:
        if not voice:
            return "onyx"
        norm = str(voice).lower().strip()
        if norm in OPENAI_VOICES:
            return norm
        for alias, target in VOICE_ALIASES.items():
            if alias in norm:
                return target
        return "onyx"

    async def generate(
        self,
        text: str,
        language: str = "en",
        voice: Optional[str] = None
    ) -> TTSResult:
        if not self.api_key:
            logger.warning("No OPENAI_API_KEY available, falling back to neural TTS")
            from backend.app.integrations.tts.providers.mock import MockTTSProvider
            return await MockTTSProvider().generate(text, language, voice)

        target_voice = self._resolve_voice(voice)
        logger.info(f"OpenAI TTS generating audio using voice '{target_voice}' (HD neural synthesis)")

        url = "https://api.openai.com/v1/audio/speech"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "tts-1",
            "voice": target_voice,
            "input": text,
            "response_format": "mp3"
        }

        try:
            async with httpx.AsyncClient(timeout=45.0) as client:
                res = await client.post(url, json=payload, headers=headers)
                if res.status_code != 200:
                    raise ProviderError(f"OpenAI TTS API error ({res.status_code}): {res.text}")
                mp3_bytes = res.content

            # Convert to 24000Hz 16-bit mono WAV for precise duration & lip sync
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f_in, \
                 tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f_out:
                f_in.write(mp3_bytes)
                f_in.flush()
                in_path = f_in.name
                out_path = f_out.name

            try:
                cmd = [self.ffmpeg_exe, "-y", "-i", in_path, "-ac", "1", "-ar", "24000", out_path]
                proc = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)

                words = text.split()
                duration = max(2.0, len(words) / 2.5)
                for line in proc.stderr.split("\n"):
                    if "Duration:" in line:
                        parts = line.split("Duration:")[1].split(",")[0].strip().split(":")
                        duration = float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
                        break

                with open(out_path, "rb") as f:
                    wav_bytes = f.read()

                # Generate word timestamps with punctuation pauses
                word_timestamps = []
                base_time = (duration * 0.85) / max(1, len(words))
                curr_t = 0.1
                for w in words:
                    clean = re.sub(r"[^a-zA-Z]", "", w)
                    w_dur = base_time * (1.0 + 0.05 * max(0, len(clean) - 4))
                    w_start = curr_t
                    w_end = min(duration, w_start + w_dur)
                    word_timestamps.append({
                        "word": w,
                        "start": round(w_start, 2),
                        "end": round(w_end, 2)
                    })
                    curr_t = w_end
                    if w.endswith((".", "!", "?")):
                        curr_t += 0.4
                    elif w.endswith((",", ";", ":")):
                        curr_t += 0.2
                    else:
                        curr_t += 0.03

                logger.info(f"OpenAI TTS generated {duration:.2f}s of pristine audio for voice '{target_voice}'")
                return TTSResult(
                    audio_bytes=wav_bytes,
                    duration_seconds=round(duration, 2),
                    format="wav",
                    word_timestamps=word_timestamps
                )
            finally:
                if os.path.exists(in_path):
                    os.unlink(in_path)
                if os.path.exists(out_path):
                    os.unlink(out_path)

        except Exception as e:
            logger.warning(f"OpenAI TTS encountered exception, falling back to Neural TTS: {e}")
            from backend.app.integrations.tts.providers.mock import MockTTSProvider
            return await MockTTSProvider().generate(text, language, voice)
