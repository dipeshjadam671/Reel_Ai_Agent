from typing import Any, Dict
from backend.app.agents.state import CycleState
from backend.app.media.renderer import VideoRenderer
from backend.app.core.logging import logger

async def run_editor(state: CycleState) -> Dict[str, Any]:
    workspace_id = state.get("workspace_id", "default_ws")
    cycle_id = state.get("cycle_id", "temp_cycle")
    script = state.get("script", {})
    title = script.get("title", "Video")
    scenes = script.get("scenes", [])
    voice_track = state.get("voice_track", {})
    assets = state.get("assets", [])
    presenter_clips = state.get("presenter_clips", [])
    presenter_cfg = state.get("presenter_config", {})
    layout = presenter_cfg.get("layout", "background")

    logger.info(f"Editor Agent starting FFmpeg composition for cycle {cycle_id} (layout: {layout})")

    renderer = VideoRenderer()
    voice_bytes = voice_track.get("_raw_bytes", b"")
    avatar_bytes = presenter_clips[0].get("_raw_bytes") if presenter_clips else None

    render_result = await renderer.render_cycle_video(
        workspace_id=workspace_id,
        cycle_id=cycle_id,
        title=title,
        scenes=scenes,
        voice_audio_bytes=voice_bytes,
        scene_assets=assets,
        avatar_video_bytes=avatar_bytes,
        layout=layout,
    )

    return {
        "render": render_result,
        "current_agent": "editor"
    }
