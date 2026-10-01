from typing import Any, Dict
from langgraph.types import interrupt
from backend.app.agents.state import CycleState
from backend.app.core.logging import logger

def route_after_novelty(state: CycleState) -> str:
    score = state.get("novelty_score", 1.0)
    retries = state.get("retry_count", 0)
    if score < 0.70 and retries < 2:
        logger.warning(f"Topic is not novel ({score:.2f} < 0.70). Retrying Trend Scout...")
        return "trend_scout"
    return "scriptwriter"

def route_after_qa(state: CycleState) -> str:
    compliance = state.get("compliance_result", {})
    qa = state.get("qa_result", {})

    if not compliance.get("passed", True):
        logger.error("Compliance gate rejected video. Halting publishing.")
        return "escalation_failure"

    if not qa.get("passed", True):
        retries = state.get("retry_count", 0)
        if retries < 2:
            logger.warning("QA check failed. Routing to scriptwriter for regeneration.")
            return "scriptwriter"
        return "escalation_failure"

    return "human_approval_gate"

def human_approval_gate(state: CycleState) -> Dict[str, Any]:
    cycle_id = state.get("cycle_id", "unknown")
    render = state.get("render", {})
    script = state.get("script", {})

    logger.info(f"Pausing workflow at Human Approval Gate for cycle {cycle_id}")

    # LangGraph Interrupt: persists checkpoint and yields control back to API
    user_input = interrupt({
        "type": "video_approval",
        "cycle_id": cycle_id,
        "video_url": render.get("video_url"),
        "thumbnail_url": render.get("thumbnail_url"),
        "title": script.get("title"),
        "hook": script.get("hook"),
        "feedback_required": True
    })

    # Resumed state processing
    if isinstance(user_input, dict):
        action = user_input.get("action", "approved")
        feedback = user_input.get("feedback")
    else:
        action = str(user_input)
        feedback = None

    logger.info(f"Human approval resumed with action='{action}', feedback='{feedback}'")

    return {
        "approval_status": action,
        "feedback": feedback,
        "current_agent": "human_approval_gate"
    }

def route_after_approval(state: CycleState) -> str:
    status = state.get("approval_status", "approved")
    if status == "approved":
        return "publisher"
    elif status in ("regenerate", "rejected"):
        return "scriptwriter"
    return "escalation_failure"
