from enum import Enum
from typing import Optional
from backend.app.core.config import settings
from backend.app.core.logging import logger
from backend.app.integrations.llm.base import LLMProvider, LLMResponse
from backend.app.integrations.llm.providers.mock import MockLLMProvider
from backend.app.integrations.llm.providers.openai_provider import OpenAIProvider

class TaskComplexity(str, Enum):
    CHEAP = "cheap"          # Classification, title generation, hashtag formatting
    STANDARD = "standard"    # Script writing, localization, research aggregation
    REASONING = "reasoning"  # Fact checking, novelty gating, QA critique

class LLMRouter:
    def __init__(self):
        self.is_mock = settings.MOCK_EXTERNAL_APIS

    def get_provider_for_task(self, complexity: TaskComplexity = TaskComplexity.STANDARD) -> LLMProvider:
        raw_key = settings.OPENAI_API_KEY
        clean_key = raw_key.strip("'\"") if raw_key else None
        if not clean_key:
            return MockLLMProvider(model_name=f"mock-{complexity.value}")

        if complexity == TaskComplexity.REASONING:
            return OpenAIProvider(api_key=clean_key, model_name=settings.LLM_REASONING_MODEL)
        else:
            return OpenAIProvider(api_key=clean_key, model_name=settings.LLM_CHEAP_MODEL)

    async def execute_with_fallback(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        complexity: TaskComplexity = TaskComplexity.STANDARD,
        json_mode: bool = False,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        primary = self.get_provider_for_task(complexity)
        try:
            return await primary.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                json_mode=json_mode,
                temperature=temperature,
                max_tokens=max_tokens,
            )
        except Exception as e:
            logger.warning(
                f"Primary LLM provider failed ({str(e)}). Engaging fallback provider...",
                extra={"event": "llm_fallback", "status": "engaging_fallback", "duration": 0, "cost": 0}
            )
            fallback = MockLLMProvider(model_name="fallback-mock")
            return await fallback.generate(
                prompt=prompt,
                system_prompt=system_prompt,
                json_mode=json_mode,
                temperature=temperature,
                max_tokens=max_tokens,
            )

llm_router = LLMRouter()
