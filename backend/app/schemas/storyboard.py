from typing import List, Optional
from pydantic import BaseModel

class StoryboardScene(BaseModel):
    scene_number: int
    duration_seconds: float
    visual_prompt: str
    media_type: str  # "video" or "image"
    transition: str  # "fade", "zoom", "cut"
    subtitle_style: str  # "karaoke_pop", "clean"
    camera_angle: str  # "medium_close_up", "wide"

class StoryboardOutput(BaseModel):
    total_duration_seconds: float
    scenes: List[StoryboardScene]
    music_mood: str
    target_bpm: int
