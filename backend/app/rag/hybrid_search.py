from typing import List, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.rag.vector_store import VectorStore
from backend.app.db.models.chunks import DocChunk

class HybridSearchEngine:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.vector_store = VectorStore(session)

    async def search(
        self,
        workspace_id: str,
        query: str,
        top_k: int = 5
    ) -> List[Tuple[DocChunk, float]]:
        # Vector score
        vector_results = await self.vector_store.search_similar_docs(workspace_id, query, top_k=top_k * 2)

        # Keyword / BM25 token overlap score
        query_tokens = set(query.lower().split())
        combined = []
        for doc, vec_score in vector_results:
            doc_tokens = set(doc.content.lower().split())
            overlap = len(query_tokens.intersection(doc_tokens)) / max(1, len(query_tokens))
            hybrid_score = (0.7 * vec_score) + (0.3 * overlap)
            combined.append((doc, round(hybrid_score, 4)))

        combined.sort(key=lambda x: x[1], reverse=True)
        return combined[:top_k]
