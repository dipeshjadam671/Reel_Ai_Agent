from typing import Any, Dict
from backend.app.agents.state import CycleState
from backend.app.agents.publishing.publisher import run_publisher
from backend.app.agents.analytics.analytics import run_analytics

class PublishingWorkflow:
    async def run(self, state: CycleState) -> Dict[str, Any]:
        pub_out = await run_publisher(state)
        state.update(pub_out)

        analytics_out = await run_analytics(state)
        state.update(analytics_out)

        return state
