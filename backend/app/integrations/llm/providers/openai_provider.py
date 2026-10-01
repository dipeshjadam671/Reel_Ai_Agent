import json
import time
from typing import Optional
import httpx
from backend.app.integrations.llm.base import LLMProvider, LLMResponse
from backend.app.core.exceptions import ProviderError
from backend.app.core.config import settings

class OpenAIProvider(LLMProvider):
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gpt-4o"):
        raw_key = api_key or settings.OPENAI_API_KEY
        self.api_key = raw_key.strip("'\"") if raw_key else None
        self.model_name = model_name
        self.base_url = "https://api.openai.com/v1"

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_mode: bool = False,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        if not self.api_key:
            raise ProviderError("OpenAI API key not configured")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model_name,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        start = time.time()
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                res = await client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
                if res.status_code != 200:
                    raise ProviderError(f"OpenAI error: {res.text}")
                data = res.json()

            choice = data["choices"][0]
            usage = data.get("usage", {})
            in_tokens = usage.get("prompt_tokens", 0)
            out_tokens = usage.get("completion_tokens", 0)
            cost = (in_tokens * 0.0000025) + (out_tokens * 0.000010)

            return LLMResponse(
                content=choice["message"]["content"],
                model=self.model_name,
                input_tokens=in_tokens,
                output_tokens=out_tokens,
                cost_usd=cost,
                latency_ms=(time.time() - start) * 1000.0,
            )
        except Exception as e:
            if isinstance(e, ProviderError):
                raise
            raise ProviderError(f"OpenAI request failed: {str(e)}")
