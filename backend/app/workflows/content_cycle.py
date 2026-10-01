from typing import Any, Dict, Optional
from langgraph.types import Command
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.agents.graph import cycle_graph
from backend.app.agents.state import CycleState
from backend.app.core.constants import CycleStatus
from backend.app.core.logging import logger
from backend.app.db.models.cycle import Cycle
from backend.app.db.models.script import Script
from backend.app.db.models.source import Source
from backend.app.db.models.asset import Asset
from backend.app.db.models.render import Render
from backend.app.db.models.publication import Publication
from backend.app.db.repositories.cycle_repository import CycleRepository
from backend.app.services.cost_service import CostService
from backend.app.rag.memory import AgentMemory

class ContentCycleWorkflow:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.cycle_repo = CycleRepository(session)
        self.cost_service = CostService(session)
        self.memory = AgentMemory(session)

    async def execute_cycle(self, workspace_id: str, cycle_id: str) -> Dict[str, Any]:
        cycle = await self.cycle_repo.get_by_id(workspace_id, cycle_id)
        if not cycle:
            raise ValueError(f"Cycle {cycle_id} not found")

        task = cycle.task
        initial_state: CycleState = {
            "cycle_id": cycle.id,
            "task_id": task.id,
            "workspace_id": workspace_id,
            "thread_id": cycle.thread_id,
            "topic": task.topic,
            "seed_script": task.seed_script or "",
            "language": task.language,
            "platforms": task.target_platforms or ["youtube"],
            "presenter_config": task.presenter_config or {},
            "brand_preferences": task.brand_preferences or {},
            "retry_count": 0,
            "estimated_cost": 0.0,
            "actual_cost": 0.0,
            "errors": []
        }

        config = {"configurable": {"thread_id": cycle.thread_id}}
        logger.info(f"Starting LangGraph content cycle execution for cycle {cycle_id} (Thread: {cycle.thread_id})")

        cycle.status = CycleStatus.RESEARCHING.value
        await self.cycle_repo.update(cycle)

        # Run graph until interrupt or end
        state_output = await cycle_graph.ainvoke(initial_state, config=config)

        # Sync resulting state with database
        await self._sync_state_to_db(workspace_id, cycle, state_output)
        return state_output

    async def resume_with_approval(
        self,
        workspace_id: str,
        cycle_id: str,
        action: str,  # "approved", "rejected", "regenerate"
        feedback: Optional[str] = None
    ) -> Dict[str, Any]:
        cycle = await self.cycle_repo.get_by_id(workspace_id, cycle_id)
        if not cycle:
            raise ValueError(f"Cycle {cycle_id} not found")

        logger.info(f"Resuming cycle {cycle_id} from human approval gate with action='{action}'")
        config = {"configurable": {"thread_id": cycle.thread_id}}

        decision = {"action": action, "feedback": feedback}
        state_output = await cycle_graph.ainvoke(Command(resume=decision), config=config)

        await self._sync_state_to_db(workspace_id, cycle, state_output)
        return state_output

    async def _sync_state_to_db(self, workspace_id: str, cycle: Cycle, state: Dict[str, Any]):
        cycle.current_agent = state.get("current_agent")
        cycle.novelty_score = state.get("novelty_score")

        # Save Sources
        if state.get("sources") and not cycle.sources:
            for s in state["sources"]:
                src = Source(
                    workspace_id=workspace_id,
                    cycle_id=cycle.id,
                    title=s.get("title", ""),
                    url=s.get("url", ""),
                    domain=s.get("domain", ""),
                    summary=s.get("summary", ""),
                    claims={"claims": state.get("claims", [])},
                    credibility_score=s.get("credibility_score", 1.0)
                )
                self.session.add(src)

        # Save Script
        if state.get("script") and not cycle.script:
            sc = state["script"]
            script_rec = Script(
                workspace_id=workspace_id,
                cycle_id=cycle.id,
                title=sc.get("title", ""),
                hook=sc.get("hook", ""),
                raw_content=sc.get("hook", ""),
                language=sc.get("language", "en"),
                scenes=sc.get("scenes", []),
                claims=sc.get("claims", []),
                call_to_action=sc.get("call_to_action", ""),
                version=1
            )
            self.session.add(script_rec)
            cycle.script = script_rec

            # Store in Agent long-term memory for novelty detection
            await self.memory.remember_script(
                workspace_id=workspace_id,
                cycle_id=cycle.id,
                topic=sc.get("title", state.get("topic", "AI Video")),
                hook=sc.get("hook", ""),
                content=sc.get("hook", ""),
                claims=sc.get("claims", [])
            )

        # Save Assets
        if state.get("assets") and not cycle.assets:
            for a in state["assets"]:
                asset_rec = Asset(
                    workspace_id=workspace_id,
                    cycle_id=cycle.id,
                    asset_type=a.get("asset_type", "video"),
                    provider=a.get("provider", "pexels"),
                    external_id=a.get("external_id", ""),
                    storage_url=a.get("storage_url", ""),
                    license_type=a.get("license_type", "commercial_use_allowed"),
                    license_url=a.get("license_url"),
                    attribution_text=a.get("attribution_text"),
                    duration_seconds=a.get("duration_seconds")
                )
                self.session.add(asset_rec)

        # Save Render
        if state.get("render") and not cycle.render:
            r = state["render"]
            render_rec = Render(
                workspace_id=workspace_id,
                cycle_id=cycle.id,
                video_url=r.get("video_url", ""),
                thumbnail_url=r.get("thumbnail_url"),
                captions_url=r.get("captions_url"),
                resolution=r.get("resolution", "1080x1920"),
                aspect_ratio=r.get("aspect_ratio", "9:16"),
                duration_seconds=r.get("duration_seconds", 0.0),
                file_size_bytes=r.get("file_size_bytes", 0),
                render_time_seconds=r.get("render_time_seconds", 0.0),
                c2pa_manifest_id=r.get("c2pa_manifest_id")
            )
            self.session.add(render_rec)
            cycle.render = render_rec

        # Update Cycle Status
        if state.get("publications"):
            cycle.status = CycleStatus.PUBLISHED.value
            for pub in state["publications"]:
                pub_rec = Publication(
                    workspace_id=workspace_id,
                    cycle_id=cycle.id,
                    platform=pub.get("platform", "youtube"),
                    status=pub.get("status", "published"),
                    platform_post_id=pub.get("platform_post_id"),
                    permalink=pub.get("permalink"),
                    metadata_payload=pub.get("metadata_payload", {}),
                    error_message=pub.get("error_message")
                )
                self.session.add(pub_rec)
        elif state.get("current_agent") == "human_approval_gate":
            cycle.status = CycleStatus.PENDING_APPROVAL.value
        elif state.get("approval_status") == "rejected":
            cycle.status = CycleStatus.REJECTED.value
        elif state.get("render"):
            cycle.status = CycleStatus.PENDING_APPROVAL.value
        else:
            cycle.status = CycleStatus.PRODUCING.value

        # Record spend
        await self.cost_service.record_spend(
            workspace_id=workspace_id,
            provider="langgraph_pipeline",
            operation="mock_operation",
            units=1.0,
            cycle_id=cycle.id,
            is_mock=True
        )

        await self.cycle_repo.update(cycle)
        await self.session.commit()
        await self.session.refresh(cycle)
