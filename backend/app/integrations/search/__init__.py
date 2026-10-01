from backend.app.core.config import settings
from backend.app.integrations.search.base import SearchProvider
from backend.app.integrations.search.providers.mock import MockSearchProvider
from backend.app.integrations.search.providers.duckduckgo import DuckDuckGoSearchProvider
from backend.app.integrations.search.providers.tavily import TavilySearchProvider

def get_search_provider() -> SearchProvider:
    if settings.TAVILY_API_KEY and settings.TAVILY_API_KEY.strip("'\""):
        return TavilySearchProvider()
    if settings.MOCK_EXTERNAL_APIS or settings.SEARCH_PROVIDER == "mock":
        return MockSearchProvider()
    return DuckDuckGoSearchProvider()

