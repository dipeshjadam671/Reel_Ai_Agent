import io
import math
import os
import struct
import subprocess
import tempfile
import wave
from typing import Optional
import imageio_ffmpeg
from backend.app.integrations.tts.base import TTSProvider, TTSResult
from backend.app.core.logging import logger

VOICE_MAP = {
    "hi": "hi-IN-MadhurNeural",
    "hi-in": "hi-IN-MadhurNeural",
    "en": "en-US-GuyNeural",
    "en-us": "en-US-GuyNeural",
    "es": "es-ES-AlvaroNeural",
    "fr": "fr-FR-HenriNeural",
    "de": "de-DE-ConradNeural",
}

def create_synthetic_wav(duration_seconds: float, sample_rate: int = 24000) -> bytes:
    num_samples = int(duration_seconds * sample_rate)
    buffer = io.BytesIO()
    with wave.open(buffer, "wb") as wav_file:
        wav_file.setnchannels(1)      # Mono
        wav_file.setsampwidth(2)     # 16-bit
        wav_file.setframerate(sample_rate)

        # Generate a gentle soft 440Hz sine wave tone with envelope
        for i in range(num_samples):
            t = float(i) / sample_rate
            amplitude = 3000.0 * (0.5 + 0.5 * math.sin(2 * math.pi * 3.0 * t))
            sample = int(amplitude * math.sin(2 * math.pi * 440.0 * t))
            wav_file.writeframesraw(struct.pack("<h", max(-32767, min(32767, sample))))

    return buffer.getvalue()

class MockTTSProvider(TTSProvider):
    async def generate(
        self,
        text: str,
        language: str = "en",
        voice: Optional[str] = None
    ) -> TTSResult:
        words = text.split()

        # Try high-quality neural edge_tts first
        try:
            import edge_tts
            lang_key = language.lower() if language else "en"
            edge_voice = VOICE_MAP.get(lang_key, "en-US-GuyNeural")
            v_lower = str(voice or "").lower()
            if any(f in v_lower for f in ["rachel", "bella", "sarah", "priya", "swara", "female", "nova", "aria", "shimmer"]):
                if lang_key.startswith("hi"):
                    edge_voice = "hi-IN-SwaraNeural"
                else:
                    edge_voice = "en-US-AriaNeural"
            elif any(f in v_lower for f in ["guy", "onyx", "echo", "davis", "alex", "leo", "male"]):
                edge_voice = "en-US-GuyNeural"

            communicate = edge_tts.Communicate(text, edge_voice)
            audio_chunks = bytearray()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_chunks.extend(chunk["data"])

            if audio_chunks:
                ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
                with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f_in, \
                     tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f_out:
                    f_in.write(audio_chunks)
                    f_in.flush()
                    in_path = f_in.name
                    out_path = f_out.name

                cmd = [ffmpeg_exe, "-y", "-i", in_path, "-ac", "1", "-ar", "24000", out_path]
                proc = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)

                duration = max(3.0, len(words) / 2.5)
                for line in proc.stderr.split("\n"):
                    if "Duration:" in line:
                        parts = line.split("Duration:")[1].split(",")[0].strip().split(":")
                        duration = float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
                        break

                with open(out_path, "rb") as f:
                    wav_bytes = f.read()

                if os.path.exists(in_path):
                    os.unlink(in_path)
                if os.path.exists(out_path):
                    os.unlink(out_path)

                word_timestamps = []
                time_per_word = duration / max(1, len(words))
                curr_time = 0.0
                for w in words:
                    word_timestamps.append({
                        "word": w,
                        "start": round(curr_time, 2),
                        "end": round(curr_time + time_per_word, 2)
                    })
                    curr_time += time_per_word

                logger.info(f"Generated realistic neural speech: {duration:.1f}s via {edge_voice}")
                return TTSResult(
                    audio_bytes=wav_bytes,
                    duration_seconds=round(duration, 2),
                    format="wav",
                    word_timestamps=word_timestamps
                )
        except Exception as e:
            logger.warning(f"EdgeTTS generation fallback: {e}")

        # Fallback to synthetic audio if edge_tts is unavailable
        duration = max(2.0, len(words) / 2.5)
        audio_bytes = create_synthetic_wav(duration)

        word_timestamps = []
        time_per_word = duration / max(1, len(words))
        curr_time = 0.0
        for w in words:
            word_timestamps.append({
                "word": w,
                "start": round(curr_time, 2),
                "end": round(curr_time + time_per_word, 2)
            })
            curr_time += time_per_word

        return TTSResult(
            audio_bytes=audio_bytes,
            duration_seconds=round(duration, 2),
            format="wav",
            word_timestamps=word_timestamps
        )
