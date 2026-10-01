from typing import Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.rag.vector_store import VectorStore

class NoveltyDetector:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.vector_store = VectorStore(session)

    async def evaluate_novelty(self, workspace_id: str, candidate_text: str) -> Tuple[float, str]:
        """
        Returns (novelty_score, explanation).
        novelty_score is in range 0.0 (exact duplicate) to 1.0 (completely new angle).
        """
        matches = await self.vector_store.search_similar_scripts(workspace_id, candidate_text, top_k=1)
        if not matches:
            return (0.95, "Completely fresh topic. No previous scripts recorded in workspace.")

        top_match, similarity = matches[0]
        novelty_score = max(0.0, min(1.0, 1.0 - similarity))

        if novelty_score >= 0.70:
            return (round(novelty_score, 2), f"Angle is novel. Max similarity to script '{top_match.topic}' is {similarity:.2f}.")
        else:
            return (round(novelty_score, 2), f"Angle overlaps significantly with previous script '{top_match.topic}' (similarity: {similarity:.2f}).")
