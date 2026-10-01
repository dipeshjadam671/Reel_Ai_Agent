from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class CycleRunRequest(BaseModel):
    override_topic: Optional[str] = None
    override_language: Optional[str] = None

class CycleStatusOut(BaseModel):
    cycle_id: str
    status: str
    current_agent: Optional[str] = None
    novelty_score: Optional[float] = None
    estimated_cost_usd: float
    actual_cost_usd: float
    updated_at: datetime

class CyclePreviewOut(BaseModel):
    cycle_id: str
    status: str
    topic: str
    language: str
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    captions_url: Optional[str] = None
    duration_seconds: float = 0.0
    resolution: str = "1080x1920"
    title: Optional[str] = None
    hook: Optional[str] = None
    call_to_action: Optional[str] = None
    qa_score: Optional[float] = None
    compliance_passed: bool = False

class CycleOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    task_id: str
    thread_id: str
    status: str
    current_agent: Optional[str] = None
    novelty_score: Optional[float] = None
    estimated_cost_usd: float
    actual_cost_usd: float
    error_details: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime

    # Rich Reel metadata
    topic: Optional[str] = None
    task_name: Optional[str] = None
    reel_title: Optional[str] = None
    presenter_avatar_id: Optional[str] = None
    video_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
