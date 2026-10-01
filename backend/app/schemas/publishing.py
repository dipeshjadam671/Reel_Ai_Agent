from typing import Any, Dict, List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class SocialConnectRequest(BaseModel):
    platform: str
    auth_code: str
    redirect_uri: Optional[str] = None

class SocialAccountOut(BaseModel):
    platform: str
    account_name: str
    connected: bool
    last_synced: Optional[datetime] = None

class PublicationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    cycle_id: str
    platform: str
    status: str
    platform_post_id: Optional[str] = None
    permalink: Optional[str] = None
    published_at: Optional[datetime] = None
    error_message: Optional[str] = None
    views: int = 0
    likes: int = 0
    shares: int = 0
