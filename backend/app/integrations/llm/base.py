from typing import Any, Dict, Optional, Protocol, runtime_checkable
from pydantic import BaseModel

class LLMResponse(BaseModel):
    content: str
    model: str
    input_tokens: int = 0
    output_tokens: int = 0
    cost_usd: float = 0.0
    latency_ms: float = 0.0

@runtime_checkable
class LLMProvider(Protocol):
    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_mode: bool = False,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        ...
