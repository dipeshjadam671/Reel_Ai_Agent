import math
from typing import Any, Dict, List, Optional

def format_timestamp_srt(seconds: float) -> str:
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{millis:03d}"

def format_timestamp_ass(seconds: float) -> str:
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    centis = int((seconds - int(seconds)) * 100)
    return f"{hrs:d}:{mins:02d}:{secs:02d}.{centis:02d}"

class SubtitleGenerator:
    def generate_srt(self, scenes: List[Dict[str, Any]], total_duration: Optional[float] = None) -> str:
        srt_lines = []
        index = 1
        curr_time = 0.0

        raw_total = sum(max(2.0, float(sc.get("duration_seconds", 4.0))) for sc in scenes)
        scale = (total_duration / raw_total) if total_duration and raw_total > 0 else 1.0

        for sc in scenes:
            scene_dur = max(2.0, float(sc.get("duration_seconds", 4.0))) * scale
            raw_text = (sc.get("on_screen_text") or sc.get("voiceover_text", "")).strip()
            # Clean emojis to prevent hollow square glyphs in libass rendering
            import re
            text = re.sub(r"[\U00010000-\U0010ffff\u2600-\u27bf\u2300-\u23ff]", "", raw_text).strip()

            words = text.split()
            if not words:
                curr_time += scene_dur
                continue

            # Chunk into punchy short phrases (4-5 words max) for vertical video
            chunk_size = 5
            chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
            chunk_dur = scene_dur / len(chunks)

            for chunk in chunks:
                start_ts = format_timestamp_srt(curr_time)
                end_ts = format_timestamp_srt(curr_time + chunk_dur)

                srt_lines.append(f"{index}")
                srt_lines.append(f"{start_ts} --> {end_ts}")
                srt_lines.append(chunk)
                srt_lines.append("")

                index += 1
                curr_time += chunk_dur

        return "\n".join(srt_lines)

    def generate_ass(self, scenes: List[Dict[str, Any]], primary_color: str = "&H00FFFFFF") -> str:
        """
        Generates Advanced SubStation Alpha format with animated centered modern vertical subtitles.
        """
        header = f"""[Script Info]
Title: Autonomous Video AI Subtitles
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,64,{primary_color},&H000000FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,4,2,2,60,60,400,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        events = []
        curr_time = 0.0
        for sc in scenes:
            dur = sc.get("duration_seconds", 4.0)
            text = sc.get("on_screen_text") or sc.get("voiceover_text", "")
            start_ts = format_timestamp_ass(curr_time)
            end_ts = format_timestamp_ass(curr_time + dur)
            # Add subtle bounce effect tag
            clean_text = text.strip().replace("\n", " ")
            events.append(f"Dialogue: 0,{start_ts},{end_ts},Default,,0,0,0,,{{\\fad(150,150)}}{clean_text}")
            curr_time += dur

        return header + "\n".join(events)

subtitle_generator = SubtitleGenerator()
