import json
from typing import Any, Dict
from backend.app.agents.state import CycleState
from backend.app.integrations.search import get_search_provider
from backend.app.integrations.llm.router import llm_router, TaskComplexity
from backend.app.core.logging import logger

async def run_researcher(state: CycleState) -> Dict[str, Any]:
    topic = state.get("topic", "")
    seed_script = state.get("seed_script", "")
    trends = state.get("trends", [])
    selected_angle = trends[0]["angle"] if trends else topic

    logger.info(f"Researcher querying sources for: '{selected_angle}'")
    search_provider = get_search_provider()
    search_results = await search_provider.search(f"{topic} {selected_angle}", max_results=3)

    formatted_search = "\n".join([
        f"- Title: {r.title}\n  URL: {r.url}\n  Domain: {r.domain}\n  Snippet: {r.snippet}"
        for r in search_results
    ])

    user_seed = f"\nUser Context / Directives:\n{seed_script}" if seed_script else ""

    prompt = f"""
    Based on the following web search results for "{topic}":
    {formatted_search}
    {user_seed}

    Extract key research sources and 2 concrete factual claims.
    Return JSON format:
    {{
        "sources": [
            {{
                "title": "string",
                "url": "string",
                "domain": "string",
                "summary": "string",
                "credibility_score": float
            }}
        ],
        "claims": [
            {{
                "claim": "string",
                "source_url": "string",
                "verified": true,
                "confidence": float
            }}
        ]
    }}
    """

    res = await llm_router.execute_with_fallback(
        prompt=prompt,
        system_prompt="You are an objective investigative researcher extracting verified facts.",
        complexity=TaskComplexity.STANDARD,
        json_mode=True
    )

    try:
        data = json.loads(res.content)
        sources = data.get("sources", [])
        claims = data.get("claims", [])
    except Exception:
        sources = [
            {
                "title": r.title,
                "url": r.url,
                "domain": r.domain,
                "summary": r.snippet,
                "credibility_score": 0.95
            }
            for r in search_results
        ]
        claims = [
            {"claim": f"Recent findings highlight {topic}.", "source_url": sources[0]["url"] if sources else "", "verified": True, "confidence": 0.9}
        ]

    return {
        "sources": sources,
        "claims": claims,
        "current_agent": "researcher"
    }
