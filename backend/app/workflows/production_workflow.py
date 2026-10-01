from typing import Any, Dict
from backend.app.agents.state import CycleState
from backend.app.agents.production.voice import run_voice_agent
from backend.app.agents.production.presenter import run_presenter_agent
from backend.app.agents.production.caption import run_caption_agent
from backend.app.agents.production.thumbnail import run_thumbnail_agent
from backend.app.agents.production.editor import run_editor

class ProductionWorkflow:
    async def run(self, state: CycleState) -> Dict[str, Any]:
        voice_out = await run_voice_agent(state)
        state.update(voice_out)

        presenter_out = await run_presenter_agent(state)
        state.update(presenter_out)

        caption_out = await run_caption_agent(state)
        state.update(caption_out)

        thumb_out = await run_thumbnail_agent(state)
        state.update(thumb_out)

        editor_out = await run_editor(state)
        state.update(editor_out)

        return state
