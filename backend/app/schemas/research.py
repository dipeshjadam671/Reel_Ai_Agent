from typing import Any, Dict, List, Optional
from pydantic import BaseModel

class TrendItem(BaseModel):
    angle: str
    search_volume: str
    relevance_score: float
    viral_hook_idea: str

class SourceItem(BaseModel):
    title: str
    url: str
    domain: str
    summary: Optional[str] = None
    credibility_score: float = 1.0

class ClaimItem(BaseModel):
    claim: str
    source_url: str
    verified: bool = True
    confidence: float = 1.0

class ResearchOutput(BaseModel):
    topic: str
    trends: List[TrendItem]
    sources: List[SourceItem]
    claims: List[ClaimItem]
