from typing import Any, Dict
from backend.app.agents.state import CycleState
from backend.app.agents.research.trend_scout import run_trend_scout
from backend.app.agents.research.researcher import run_researcher
from backend.app.agents.research.novelty_guard import run_novelty_guard

class ResearchWorkflow:
    async def run(self, state: CycleState) -> Dict[str, Any]:
        trends_out = await run_trend_scout(state)
        state.update(trends_out)

        research_out = await run_researcher(state)
        state.update(research_out)

        novelty_out = await run_novelty_guard(state)
        state.update(novelty_out)

        return state
