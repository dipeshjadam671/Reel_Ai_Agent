import os
import pytest
from backend.app.media.subtitles import subtitle_generator
from backend.app.integrations.tts.providers.mock import MockTTSProvider
from backend.app.media.ffmpeg import ffmpeg_engine
from backend.app.media.audio import audio_processor

def test_subtitle_generation():
    scenes = [
        {"scene_number": 1, "duration_seconds": 3.0, "voiceover_text": "Scene one text", "on_screen_text": "SCENE 1"},
        {"scene_number": 2, "duration_seconds": 4.0, "voiceover_text": "Scene two text", "on_screen_text": "SCENE 2"}
    ]
    srt = subtitle_generator.generate_srt(scenes)
    assert "00:00:00,000 --> 00:00:03,000" in srt
    assert "SCENE 1" in srt
    assert "SCENE 2" in srt

    ass = subtitle_generator.generate_ass(scenes)
    assert "[Script Info]" in ass
    assert "Dialogue: 0," in ass

@pytest.mark.asyncio
async def test_audio_synthesis_and_ffmpeg_render():
    tts = MockTTSProvider()
    tts_res = await tts.generate("Testing autonomous video render pipeline with synthetic audio.", language="en")
    assert len(tts_res.audio_bytes) > 0
    assert tts_res.duration_seconds > 0

    # Write temp audio file
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(tts_res.audio_bytes)
        audio_path = f.name

    try:
        # Render a quick 2-second vertical MP4
        output_mp4 = await ffmpeg_engine.render_video(
            scene_video_paths=[],
            audio_path=audio_path,
            duration=2.0
        )
        assert os.path.exists(output_mp4)
        assert os.path.getsize(output_mp4) > 1000

        # Extract thumbnail
        thumb = await ffmpeg_engine.extract_thumbnail(output_mp4, timestamp=0.5)
        assert os.path.exists(thumb)
        assert os.path.getsize(thumb) > 500

        if os.path.exists(output_mp4):
            os.unlink(output_mp4)
        if os.path.exists(thumb):
            os.unlink(thumb)
    finally:
        if os.path.exists(audio_path):
            os.unlink(audio_path)
