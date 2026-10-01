from typing import List, Optional
from urllib.parse import urlparse
import httpx
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.integrations.search.base import SearchProvider, SearchResultItem

class TavilySearchProvider(SearchProvider):
    def __init__(self, api_key: Optional[str] = None):
        raw_key = api_key or settings.TAVILY_API_KEY
        self.api_key = raw_key.strip("'\"") if raw_key else None
        self.endpoint = "https://api.tavily.com/search"

    async def search(self, query: str, max_results: int = 5) -> List[SearchResultItem]:
        if not self.api_key:
            logger.warning("Tavily API key not found, returning empty search results")
            return []

        payload = {
            "api_key": self.api_key,
            "query": query,
            "max_results": max_results,
            "search_depth": "basic",
            "include_answer": False
        }

        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                res = await client.post(self.endpoint, json=payload)
                if res.status_code != 200:
                    logger.warning(f"Tavily search failed ({res.status_code}): {res.text}")
                    return []

                data = res.json()
                results = []
                for item in data.get("results", []):
                    url = item.get("url", "")
                    domain = urlparse(url).netloc or "web"
                    results.append(
                        SearchResultItem(
                            title=item.get("title", ""),
                            url=url,
                            snippet=item.get("content", ""),
                            domain=domain
                        )
                    )
                if results:
                    return results
                from backend.app.integrations.search.providers.duckduckgo import DuckDuckGoSearchProvider
                return await DuckDuckGoSearchProvider().search(query, max_results)
        except Exception as e:
            logger.warning(f"Tavily search query '{query}' failed ({str(e)}). Falling back to DuckDuckGo...")
            from backend.app.integrations.search.providers.duckduckgo import DuckDuckGoSearchProvider
            return await DuckDuckGoSearchProvider().search(query, max_results)
