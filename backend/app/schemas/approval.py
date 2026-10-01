from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class ApprovalActionRequest(BaseModel):
    action: str  # "approved", "rejected", "regenerate"
    feedback: Optional[str] = None

class ApprovalOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    cycle_id: str
    user_id: Optional[str] = None
    action: str
    feedback: Optional[str] = None
    created_at: datetime
