from typing import Any, Dict
from backend.app.agents.state import CycleState
from backend.app.agents.scripting.scriptwriter import run_scriptwriter
from backend.app.agents.scripting.localization import run_localization
from backend.app.agents.scripting.fact_checker import run_fact_checker

class ScriptingWorkflow:
    async def run(self, state: CycleState) -> Dict[str, Any]:
        script_out = await run_scriptwriter(state)
        state.update(script_out)

        loc_out = await run_localization(state)
        state.update(loc_out)

        fact_out = await run_fact_checker(state)
        state.update(fact_out)

        return state
