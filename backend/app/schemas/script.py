from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, ConfigDict

class SceneItem(BaseModel):
    scene_number: int
    duration_seconds: float
    visual_description: str
    voiceover_text: str
    on_screen_text: Optional[str] = None
    presenter_visible: bool = True
    background_query: str

class ScriptCreate(BaseModel):
    title: str
    hook: str
    language: str
    scenes: List[SceneItem]
    claims: List[Union[Dict[str, Any], str, Any]] = []
    call_to_action: str

class ScriptOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    cycle_id: str
    title: str
    hook: str
    raw_content: str
    language: str
    scenes: List[Dict[str, Any]]
    claims: List[Union[Dict[str, Any], str, Any]] = []
    call_to_action: str
    version: int
