from typing import Any, Dict
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver

from backend.app.agents.state import CycleState
from backend.app.agents.research.trend_scout import run_trend_scout
from backend.app.agents.research.researcher import run_researcher
from backend.app.agents.research.novelty_guard import run_novelty_guard
from backend.app.agents.scripting.scriptwriter import run_scriptwriter
from backend.app.agents.scripting.localization import run_localization
from backend.app.agents.scripting.fact_checker import run_fact_checker
from backend.app.agents.media.storyboard import run_storyboard
from backend.app.agents.media.asset_curator import run_asset_curator
from backend.app.agents.media.music_selector import run_music_selector
from backend.app.agents.production.voice import run_voice_agent
from backend.app.agents.production.presenter import run_presenter_agent
from backend.app.agents.production.caption import run_caption_agent
from backend.app.agents.production.thumbnail import run_thumbnail_agent
from backend.app.agents.production.editor import run_editor
from backend.app.agents.compliance.compliance import run_compliance
from backend.app.agents.qa.critic import run_qa_critic
from backend.app.agents.publishing.publisher import run_publisher
from backend.app.agents.analytics.analytics import run_analytics
from backend.app.agents.supervisor import (
    human_approval_gate,
    route_after_novelty,
    route_after_qa,
    route_after_approval,
)

async def escalation_failure_node(state: CycleState) -> Dict[str, Any]:
    return {
        "status": "failed",
        "current_agent": "escalation_failure",
        "errors": [{"code": "WORKFLOW_HALTED", "message": "Workflow terminated due to compliance or quality rejection"}]
    }

def build_cycle_graph():
    builder = StateGraph(CycleState)

    # 1. Research Subgraph Nodes
    builder.add_node("trend_scout", run_trend_scout)
    builder.add_node("researcher", run_researcher)
    builder.add_node("novelty_guard", run_novelty_guard)

    # 2. Scripting Subgraph Nodes
    builder.add_node("scriptwriter", run_scriptwriter)
    builder.add_node("localization", run_localization)
    builder.add_node("fact_checker", run_fact_checker)

    # 3. Media & Production Subgraph Nodes
    builder.add_node("storyboard", run_storyboard)
    builder.add_node("asset_curator", run_asset_curator)
    builder.add_node("music_selector", run_music_selector)
    builder.add_node("voice", run_voice_agent)
    builder.add_node("presenter", run_presenter_agent)
    builder.add_node("caption", run_caption_agent)
    builder.add_node("thumbnail", run_thumbnail_agent)
    builder.add_node("editor", run_editor)

    # 4. Compliance, QA & Approval Nodes
    builder.add_node("compliance", run_compliance)
    builder.add_node("qa_critic", run_qa_critic)
    builder.add_node("human_approval_gate", human_approval_gate)

    # 5. Publishing & Analytics Nodes
    builder.add_node("publisher", run_publisher)
    builder.add_node("analytics", run_analytics)
    builder.add_node("escalation_failure", escalation_failure_node)

    # Wire Edges
    builder.add_edge(START, "trend_scout")
    builder.add_edge("trend_scout", "researcher")
    builder.add_edge("researcher", "novelty_guard")

    builder.add_conditional_edges(
        "novelty_guard",
        route_after_novelty,
        {
            "trend_scout": "trend_scout",
            "scriptwriter": "scriptwriter"
        }
    )

    builder.add_edge("scriptwriter", "localization")
    builder.add_edge("localization", "fact_checker")
    builder.add_edge("fact_checker", "storyboard")
    builder.add_edge("storyboard", "asset_curator")
    builder.add_edge("asset_curator", "music_selector")
    builder.add_edge("music_selector", "voice")
    builder.add_edge("voice", "presenter")
    builder.add_edge("presenter", "caption")
    builder.add_edge("caption", "thumbnail")
    builder.add_edge("thumbnail", "editor")
    builder.add_edge("editor", "compliance")
    builder.add_edge("compliance", "qa_critic")

    builder.add_conditional_edges(
        "qa_critic",
        route_after_qa,
        {
            "human_approval_gate": "human_approval_gate",
            "scriptwriter": "scriptwriter",
            "escalation_failure": "escalation_failure"
        }
    )

    builder.add_conditional_edges(
        "human_approval_gate",
        route_after_approval,
        {
            "publisher": "publisher",
            "scriptwriter": "scriptwriter",
            "escalation_failure": "escalation_failure"
        }
    )

    builder.add_edge("publisher", "analytics")
    builder.add_edge("analytics", END)
    builder.add_edge("escalation_failure", END)

    # Global in-memory checkpointer for thread persistence & human interrupt/resume
    memory = MemorySaver()
    return builder.compile(checkpointer=memory)

cycle_graph = build_cycle_graph()
