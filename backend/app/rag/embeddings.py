import hashlib
import math
from typing import List
from backend.app.core.config import settings

class EmbeddingService:
    def __init__(self, dimension: int = 1536):
        self.dimension = dimension

    def get_embedding(self, text: str) -> List[float]:
        """
        Generates normalized embedding.
        In mock or local mode without API keys, generates deterministic high-dimensional embeddings based on text hash.
        """
        # Deterministic pseudo-embedding for testing & mock mode
        hash_val = int(hashlib.sha256(text.encode("utf-8")).hexdigest(), 16)
        vec = []
        for i in range(self.dimension):
            val = math.sin((hash_val % 1000000) + i)
            vec.append(val)
        
        # Normalize vector
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [round(x / norm, 6) for x in vec]

embedding_service = EmbeddingService()
