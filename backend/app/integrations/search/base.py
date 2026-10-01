from typing import List, Protocol, runtime_checkable
from pydantic import BaseModel

class SearchResultItem(BaseModel):
    title: str
    url: str
    snippet: str
    domain: str

@runtime_checkable
class SearchProvider(Protocol):
    async def search(self, query: str, max_results: int = 5) -> List[SearchResultItem]:
        ...
