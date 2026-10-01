import json
from typing import Any, Dict
from backend.app.agents.state import CycleState
from backend.app.integrations.llm.router import llm_router, TaskComplexity
from backend.app.core.logging import logger

async def run_storyboard(state: CycleState) -> Dict[str, Any]:
    script = state.get("script", {})
    scenes = script.get("scenes", [])

    logger.info("Storyboard Agent translating scenes into production directions")

    prompt = f"""
    Create a complete visual storyboard for these scenes:
    {json.dumps(scenes)}

    Specify total duration, per-scene camera angle, transitions, and background music mood/BPM.
    Return JSON matching:
    {{
        "total_duration_seconds": 15.0,
        "music_mood": "modern_tech_upbeat",
        "target_bpm": 124,
        "scenes": [
            {{
                "scene_number": 1,
                "duration_seconds": 4.0,
                "visual_prompt": "string",
                "media_type": "video",
                "transition": "fade",
                "subtitle_style": "karaoke_pop",
                "camera_angle": "medium_close_up"
            }}
        ]
    }}
    """

    res = await llm_router.execute_with_fallback(
        prompt=prompt,
        system_prompt="You are an expert video creative director designing dynamic, fast-paced vertical short-form storyboards.",
        complexity=TaskComplexity.STANDARD,
        json_mode=True
    )

    try:
        storyboard = json.loads(res.content)
    except Exception:
        storyboard = {
            "total_duration_seconds": sum(sc.get("duration_seconds", 4.0) for sc in scenes),
            "music_mood": "upbeat_energetic",
            "target_bpm": 128,
            "scenes": [
                {
                    "scene_number": sc.get("scene_number", i + 1),
                    "duration_seconds": sc.get("duration_seconds", 4.0),
                    "visual_prompt": sc.get("visual_description", "Modern technology background"),
                    "media_type": "video",
                    "transition": "fade",
                    "subtitle_style": "karaoke_pop",
                    "camera_angle": "medium_close_up"
                }
                for i, sc in enumerate(scenes)
            ]
        }

    return {
        "storyboard": storyboard,
        "current_agent": "storyboard"
    }
