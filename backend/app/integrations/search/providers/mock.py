from typing import List
from urllib.parse import urlparse
from backend.app.integrations.search.base import SearchProvider, SearchResultItem

class MockSearchProvider(SearchProvider):
    async def search(self, query: str, max_results: int = 5) -> List[SearchResultItem]:
        clean_q = query.replace('"', '').strip()
        return [
            SearchResultItem(
                title=f"The Complete 2026 Guide to {clean_q}",
                url=f"https://technews-daily.com/guides/{clean_q.lower().replace(' ', '-')}",
                snippet=f"Comprehensive breakdown and latest benchmark findings regarding {clean_q}. Highlights performance gains and ecosystem evolution.",
                domain="technews-daily.com",
            ),
            SearchResultItem(
                title=f"Industry Trends: How {clean_q} is Transforming Video Content",
                url=f"https://creatorgrowth.io/articles/{clean_q.lower().replace(' ', '-')}-future",
                snippet=f"Recent surveys show a 3.5x rise in audience retention when creators leverage automated workflows focused on {clean_q}.",
                domain="creatorgrowth.io",
            ),
            SearchResultItem(
                title=f"Key Insights and Case Studies for {clean_q}",
                url=f"https://researchinsights.org/papers/{clean_q.lower().replace(' ', '-')}",
                snippet=f"Statistical analysis and empirical data analyzing best practices, common misconceptions, and strategic adoption of {clean_q}.",
                domain="researchinsights.org",
            ),
        ][:max_results]
