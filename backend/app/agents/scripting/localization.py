import json
from typing import Any, Dict
from backend.app.agents.state import CycleState
from backend.app.integrations.llm.router import llm_router, TaskComplexity
from backend.app.core.logging import logger

async def run_localization(state: CycleState) -> Dict[str, Any]:
    script = state.get("script", {})
    target_language = state.get("language", "en")

    if target_language == "en":
        logger.info("Language is English, skipping translation pass")
        return {"script": script, "current_agent": "localization"}

    logger.info(f"Localization agent adapting script to '{target_language}'")

    prompt = f"""
    Translate and idiomatically adapt the following vertical short-form video script to target language "{target_language}".
    
    LOCALIZATION DIRECTIVES:
    1. Hook & Retention: The opening hook (Scene 1) MUST remain an intense, scroll-stopping pattern interrupt in {target_language}.
    2. Spoken Cadence: Translate voiceover_text into natural, high-energy conversational creator speech (140-160 WPM) that sounds authentic when spoken aloud. For Hindi, use modern, energetic Hinglish/Hindi that Indian tech and culture creators use.
    3. On-Screen Text: Translate on_screen_text into short (2 to 4 words), bold, uppercase phrases with emojis that pop on vertical mobile screens.
    4. Exact Schema Preservation: Keep all scene_numbers, duration_seconds, presenter_visible, background_query, and claims structure identical.

    Script JSON:
    {json.dumps(script)}

    Format output as STRICT JSON matching the exact same schema with translated text.
    """

    res = await llm_router.execute_with_fallback(
        prompt=prompt,
        system_prompt="You are a top-tier multilingual viral video creator and localization director specializing in high-retention short-form video adaptation.",
        complexity=TaskComplexity.STANDARD,
        json_mode=True
    )

    try:
        localized_script = json.loads(res.content)
    except Exception:
        localized_script = script
        localized_script["language"] = target_language

    return {
        "script": localized_script,
        "current_agent": "localization"
    }
