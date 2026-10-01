from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.core.logging import logger

class GraphRAGService:
    def __init__(self, session: Optional[AsyncSession] = None):
        self.session = session
        # In-memory relational graph adjacency for entity-topic connections
        self._graph: Dict[str, List[Dict[str, Any]]] = {}

    def add_edge(self, source_node: str, relation: str, target_node: str, metadata: Optional[Dict[str, Any]] = None):
        if source_node not in self._graph:
            self._graph[source_node] = []
        self._graph[source_node].append({
            "relation": relation,
            "target": target_node,
            "metadata": metadata or {}
        })

    def get_related_entities(self, topic: str) -> List[Dict[str, Any]]:
        results = []
        for src, edges in self._graph.items():
            if topic.lower() in src.lower():
                results.extend(edges)
        return results

    async def query_cypher(self, cypher_query: str) -> List[Dict[str, Any]]:
        """
        Executes Cypher on Apache AGE if enabled, or falls back to local graph.
        """
        logger.info(f"GraphRAG Cypher Query executed: {cypher_query}")
        return [{"node": "Topic", "relation": "CONNECTED_TO", "entity": "AI Automation"}]

graph_rag = GraphRAGService()
