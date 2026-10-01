from typing import Any, Dict, List

class Reranker:
    def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_n: int = 5
    ) -> List[Dict[str, Any]]:
        query_words = set(query.lower().split())
        scored = []
        for doc in documents:
            text = (doc.get("content") or doc.get("summary") or doc.get("title") or "").lower()
            overlap = sum(1 for w in query_words if w in text)
            score = doc.get("score", 0.5) + (overlap * 0.1)
            scored.append({**doc, "rerank_score": round(score, 4)})

        scored.sort(key=lambda x: x["rerank_score"], reverse=True)
        return scored[:top_n]

reranker = Reranker()
