from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict

class CycleState(TypedDict, total=False):
    cycle_id: str
    task_id: str
    workspace_id: str
    thread_id: str

    topic: str
    seed_script: Optional[str]
    language: str
    platforms: List[str]
    brand_preferences: Dict[str, Any]
    presenter_config: Dict[str, Any]

    # Research subgraph
    trends: List[Dict[str, Any]]
    sources: List[Dict[str, Any]]
    claims: List[Dict[str, Any]]
    novelty_score: float

    # Scripting subgraph
    script: Dict[str, Any]
    storyboard: Dict[str, Any]

    # Media & Production subgraph
    assets: List[Dict[str, Any]]
    voice_track: Dict[str, Any]
    presenter_clips: List[Dict[str, Any]]
    captions: Dict[str, Any]
    hashtags: Dict[str, Any]
    render: Dict[str, Any]

    # Compliance & QA
    compliance_result: Dict[str, Any]
    qa_result: Dict[str, Any]

    # Approval Gate
    approval_status: str  # "pending", "approved", "rejected", "regenerate"
    feedback: Optional[str]

    # Publishing
    publications: List[Dict[str, Any]]

    # System & Execution metadata
    current_agent: str
    errors: List[Dict[str, Any]]
    retry_count: int
    estimated_cost: float
    actual_cost: float
