from typing import Any, Dict
from backend.app.agents.state import CycleState
from backend.app.agents.media.storyboard import run_storyboard
from backend.app.agents.media.asset_curator import run_asset_curator
from backend.app.agents.media.music_selector import run_music_selector

class MediaWorkflow:
    async def run(self, state: CycleState) -> Dict[str, Any]:
        sb_out = await run_storyboard(state)
        state.update(sb_out)

        assets_out = await run_asset_curator(state)
        state.update(assets_out)

        music_out = await run_music_selector(state)
        state.update(music_out)

        return state
