from typing import List, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.db.models.chunks import ScriptChunk, DocChunk
from backend.app.rag.embeddings import embedding_service

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    norm1 = sum(a * a for a in v1) ** 0.5
    norm2 = sum(b * b for b in v2) ** 0.5
    if norm1 == 0.0 or norm2 == 0.0:
        return 0.0
    return dot / (norm1 * norm2)

class VectorStore:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def search_similar_scripts(
        self,
        workspace_id: str,
        query_text: str,
        top_k: int = 5
    ) -> List[Tuple[ScriptChunk, float]]:
        query_emb = embedding_service.get_embedding(query_text)
        stmt = select(ScriptChunk).where(ScriptChunk.workspace_id == workspace_id)
        result = await self.session.execute(stmt)
        chunks = result.scalars().all()

        scored = []
        for ch in chunks:
            if ch.embedding:
                sim = cosine_similarity(query_emb, ch.embedding)
                scored.append((ch, sim))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]

    async def search_similar_docs(
        self,
        workspace_id: str,
        query_text: str,
        top_k: int = 5
    ) -> List[Tuple[DocChunk, float]]:
        query_emb = embedding_service.get_embedding(query_text)
        stmt = select(DocChunk).where(DocChunk.workspace_id == workspace_id)
        result = await self.session.execute(stmt)
        chunks = result.scalars().all()

        scored = []
        for ch in chunks:
            if ch.embedding:
                sim = cosine_similarity(query_emb, ch.embedding)
                scored.append((ch, sim))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]
