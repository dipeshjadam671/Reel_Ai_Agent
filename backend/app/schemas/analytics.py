from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class SpendLedgerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    cycle_id: Optional[str] = None
    provider: str
    operation: str
    units: float
    unit_cost: float
    amount: float
    currency: str
    created_at: datetime

class WorkspaceAnalyticsOut(BaseModel):
    total_videos_created: int
    total_videos_published: int
    total_views: int
    total_likes: int
    total_shares: int
    total_spend_usd: float
    monthly_budget_usd: float
    recent_spend_records: List[SpendLedgerOut]
