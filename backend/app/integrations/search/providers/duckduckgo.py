from typing import List
from urllib.parse import urlparse
import httpx
from backend.app.integrations.search.base import SearchProvider, SearchResultItem

class DuckDuckGoSearchProvider(SearchProvider):
    async def search(self, query: str, max_results: int = 5) -> List[SearchResultItem]:
        # Using DuckDuckGo instant answer / html API
        url = "https://api.duckduckgo.com/"
        params = {"q": query, "format": "json", "no_html": 1, "skip_disambig": 1}
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                res = await client.get(url, params=params)
                if res.status_code == 200:
                    data = res.json()
                    results = []
                    abstract = data.get("AbstractText")
                    if abstract:
                        source_url = data.get("AbstractURL") or "https://duckduckgo.com"
                        results.append(SearchResultItem(
                            title=data.get("Heading") or query,
                            url=source_url,
                            snippet=abstract,
                            domain=urlparse(source_url).netloc or "duckduckgo.com"
                        ))
                    for topic in data.get("RelatedTopics", [])[:max_results - len(results)]:
                        if "Text" in topic and "FirstURL" in topic:
                            results.append(SearchResultItem(
                                title=topic["Text"][:60],
                                url=topic["FirstURL"],
                                snippet=topic["Text"],
                                domain=urlparse(topic["FirstURL"]).netloc
                            ))
                    if results:
                        return results
        except Exception:
            pass

        # Fallback to Mock Search Provider
        from backend.app.integrations.search.providers.mock import MockSearchProvider
        return await MockSearchProvider().search(query, max_results)
