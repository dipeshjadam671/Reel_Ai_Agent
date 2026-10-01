from typing import Any, Dict, List
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.models.chunks import ScriptChunk
from backend.app.rag.embeddings import embedding_service

class AgentMemory:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def remember_script(
        self,
        workspace_id: str,
        cycle_id: str,
        topic: str,
        hook: str,
        content: str,
        claims: List[Dict[str, Any]]
    ) -> ScriptChunk:
        emb = embedding_service.get_embedding(f"{topic} {hook} {content}")
        chunk = ScriptChunk(
            workspace_id=workspace_id,
            cycle_id=cycle_id,
            topic=topic,
            hook=hook,
            content=content,
            embedding=emb,
            claims=claims,
        )
        self.session.add(chunk)
        await self.session.flush()
        return chunk
