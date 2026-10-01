from typing import Optional
from pydantic import BaseModel, ConfigDict

class AssetCreate(BaseModel):
    asset_type: str
    provider: str
    external_id: str
    storage_url: str
    license_type: str = "commercial_use_allowed"
    license_url: Optional[str] = None
    attribution_text: Optional[str] = None
    duration_seconds: Optional[float] = None

class AssetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    cycle_id: str
    asset_type: str
    provider: str
    external_id: str
    storage_url: str
    license_type: str
    license_url: Optional[str] = None
    attribution_text: Optional[str] = None
    duration_seconds: Optional[float] = None

class RenderOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    cycle_id: str
    video_url: str
    thumbnail_url: Optional[str] = None
    captions_url: Optional[str] = None
    resolution: str
    aspect_ratio: str
    duration_seconds: float
    file_size_bytes: int
    render_time_seconds: float
