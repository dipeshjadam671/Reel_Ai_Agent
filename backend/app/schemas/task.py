from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class PresenterConfig(BaseModel):
    avatar_id: Optional[str] = "avatar_alex"
    voice_id: Optional[str] = "voice_en_neutral"
    pose: Optional[str] = "portrait"
    layout: Optional[str] = "overlay_pip"  # "overlay_pip" or "full_screen"

class ScheduleConfig(BaseModel):
    frequency: str = "daily"  # "daily", "weekdays", "weekends", "custom"
    time: str = "09:00"
    timezone: str = "UTC"
    active_days: List[str] = Field(default_factory=lambda: ["mon", "tue", "wed", "thu", "fri"])

class BrandPreferences(BaseModel):
    tone: str = "engaging"
    color_palette: List[str] = Field(default_factory=lambda: ["#000000", "#FFFFFF", "#FF0000"])
    call_to_action: str = "Follow for daily AI insights!"
    avoid_topics: List[str] = Field(default_factory=list)

class TaskCreate(BaseModel):
    name: str
    topic: str
    seed_script: Optional[str] = None
    language: str = "en"
    target_platforms: List[str] = Field(default_factory=lambda: ["youtube", "instagram", "tiktok"])
    presenter_config: Optional[PresenterConfig] = Field(default_factory=PresenterConfig)
    schedule_config: Optional[ScheduleConfig] = Field(default_factory=ScheduleConfig)
    brand_preferences: Optional[BrandPreferences] = Field(default_factory=BrandPreferences)

class TaskUpdate(BaseModel):
    name: Optional[str] = None
    topic: Optional[str] = None
    seed_script: Optional[str] = None
    language: Optional[str] = None
    target_platforms: Optional[List[str]] = None
    presenter_config: Optional[Dict[str, Any]] = None
    schedule_config: Optional[Dict[str, Any]] = None
    brand_preferences: Optional[Dict[str, Any]] = None
    status: Optional[str] = None

class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    workspace_id: str
    name: str
    topic: str
    seed_script: Optional[str] = None
    language: str
    target_platforms: List[str]
    presenter_config: Dict[str, Any]
    schedule_config: Dict[str, Any]
    brand_preferences: Dict[str, Any]
    status: str
    latest_cycle_id: Optional[str] = None
    latest_cycle_status: Optional[str] = None
    created_at: datetime
    updated_at: datetime
