import json
import re
import asyncio
from abc import ABC, abstractmethod
from openai import AsyncOpenAI

from app.core.config import settings
from app.core.logger import get_logger
from app.core.prompts import load_prompt


class LLMService(ABC):
    def __init__(self, *, max_tokens: int = 4096):
        self.client = AsyncOpenAI(
            api_key=settings.api_key,
            base_url=settings.vllm_base_url,
        )
        self.model = settings.model_name
        self.max_tokens = max_tokens
        self.logger = get_logger(self.__class__.__name__.lower())

    async def _call_llm(
        self,
        messages: list[dict],
        *,
        max_retries: int = 3,
        max_tokens: int | None = None,
    ) -> str:
        for attempt in range(max_retries):
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=0.0,
                    max_tokens=max_tokens if max_tokens is not None else self.max_tokens,
                )
                raw = response.choices[0].message.content
                self.logger.debug(f"LLM response ({len(raw)} chars): {raw[:500]}{'...' if len(raw) > 500 else ''}")
                return raw
            except Exception as e:
                if attempt == max_retries - 1:
                    self.logger.error(f"LLM call failed after {max_retries} attempts: {type(e).__name__}: {e}")
                    raise
                self.logger.warning(f"LLM call failed (attempt {attempt + 1}/{max_retries}): {type(e).__name__}, retrying...")
                await asyncio.sleep(2 ** attempt)

    def _parse_json_with_fallback(self, raw: str, context: str) -> dict:
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            match = re.search(r"\{[\s\S]*\}", raw)
            if match:
                self.logger.warning(f"JSON parse required regex fallback in {context}")
                return json.loads(match.group())
            raise ValueError(f"Failed to parse {context} JSON: {raw[:200]}")

    def _normalize_to_string_list(self, items: list) -> list[str]:
        return [
            item["id"] if isinstance(item, dict) and "id" in item
            else item.get("location", str(item)) if isinstance(item, dict)
            else str(item)
            for item in items
        ]

    def _build_text_messages(self, prompt: str, system_prompt: str | None = None) -> list[dict]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        return messages

    def _build_vision_messages(self, image_base64: str, prompt: str) -> list[dict]:
        return [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}},
                ],
            }
        ]


class TextLLMService(LLMService):
    async def call_text(self, prompt: str, *, system_prompt: str | None = None, max_tokens: int | None = None) -> str:
        messages = self._build_text_messages(prompt, system_prompt)
        return await self._call_llm(messages, max_tokens=max_tokens)


class VisionLLMService(LLMService):
    async def call_vision(self, image_base64: str, prompt: str, max_tokens: int | None = None) -> str:
        messages = self._build_vision_messages(image_base64, prompt)
        return await self._call_llm(messages, max_tokens=max_tokens)