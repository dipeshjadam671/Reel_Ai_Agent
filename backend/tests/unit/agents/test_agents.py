import pytest
from backend.app.agents.state import CycleState
from backend.app.agents.research.trend_scout import run_trend_scout
from backend.app.agents.research.researcher import run_researcher
from backend.app.agents.research.novelty_guard import run_novelty_guard
from backend.app.agents.scripting.scriptwriter import run_scriptwriter
from backend.app.agents.scripting.localization import run_localization
from backend.app.agents.scripting.fact_checker import run_fact_checker
from backend.app.agents.media.storyboard import run_storyboard
from backend.app.agents.media.asset_curator import run_asset_curator
from backend.app.agents.compliance.compliance import run_compliance
from backend.app.agents.qa.critic import run_qa_critic
from backend.app.agents.publishing.publisher import run_publisher
from backend.app.agents.analytics.analytics import run_analytics

@pytest.mark.asyncio
async def test_trend_scout():
    state: CycleState = {"topic": "Autonomous AI Agents"}
    out = await run_trend_scout(state)
    assert "trends" in out
    assert len(out["trends"]) > 0
    assert "viral_hook_idea" in out["trends"][0]

@pytest.mark.asyncio
async def test_researcher():
    state: CycleState = {
        "topic": "Autonomous AI Agents",
        "trends": [{"angle": "Hidden Truth", "viral_hook_idea": "Did you know?"}]
    }
    out = await run_researcher(state)
    assert "sources" in out
    assert "claims" in out
    assert len(out["sources"]) > 0

@pytest.mark.asyncio
async def test_novelty_guard():
    state: CycleState = {"topic": "Autonomous AI Agents"}
    out = await run_novelty_guard(state)
    assert "novelty_score" in out
    assert out["novelty_score"] >= 0.70

@pytest.mark.asyncio
async def test_scriptwriter():
    state: CycleState = {
        "topic": "Autonomous AI Agents",
        "language": "en",
        "claims": [{"claim": "AI agents save 10 hours weekly", "verified": True}],
        "trends": [{"viral_hook_idea": "Stop scrolling!"}]
    }
    out = await run_scriptwriter(state)
    assert "script" in out
    script = out["script"]
    assert "hook" in script
    assert "scenes" in script
    assert len(script["scenes"]) > 0

@pytest.mark.asyncio
async def test_localization_hindi():
    state: CycleState = {
        "language": "hi",
        "script": {
            "title": "Autonomous AI",
            "hook": "Stop wasting time.",
            "scenes": [{"scene_number": 1, "duration_seconds": 4.0, "voiceover_text": "Stop wasting time."}],
            "call_to_action": "Follow us!"
        }
    }
    out = await run_localization(state)
    assert "script" in out
    assert out["script"]["language"] == "hi"

@pytest.mark.asyncio
async def test_storyboard_and_curator():
    state: CycleState = {
        "script": {
            "title": "Autonomous AI",
            "scenes": [
                {"scene_number": 1, "duration_seconds": 4.0, "visual_description": "Futuristic graphics"}
            ]
        }
    }
    sb_out = await run_storyboard(state)
    assert "storyboard" in sb_out
    state["storyboard"] = sb_out["storyboard"]

    curator_out = await run_asset_curator(state)
    assert "assets" in curator_out
    assert len(curator_out["assets"]) > 0
    assert "license_type" in curator_out["assets"][0]

@pytest.mark.asyncio
async def test_compliance_and_qa():
    state: CycleState = {
        "script": {"title": "Autonomous AI", "hook": "Awesome AI video"},
        "assets": [
            {
                "provider": "pexels",
                "external_id": "12345",
                "license_type": "commercial_use_allowed",
                "storage_url": "http://storage.example.com/asset.mp4"
            }
        ],
        "render": {
            "video_url": "http://storage.example.com/renders/test.mp4",
            "duration_seconds": 15.0
        }
    }
    comp_out = await run_compliance(state)
    assert comp_out["compliance_result"]["passed"] is True

    qa_out = await run_qa_critic(state)
    assert qa_out["qa_result"]["passed"] is True

@pytest.mark.asyncio
async def test_publisher_and_analytics():
    state: CycleState = {
        "platforms": ["youtube", "instagram", "tiktok"],
        "script": {"title": "Autonomous AI", "hook": "Learn AI"},
        "render": {"video_url": "http://storage.example.com/renders/test.mp4"},
        "hashtags": {"youtube": ["#AI"], "instagram": ["#reels"], "tiktok": ["#fyp"]}
    }
    pub_out = await run_publisher(state)
    assert len(pub_out["publications"]) == 3
    assert pub_out["publications"][0]["status"] == "published"

    state["publications"] = pub_out["publications"]
    analytics_out = await run_analytics(state)
    assert len(analytics_out["post_metrics"]) == 3
    assert analytics_out["post_metrics"][0]["views"] > 0
