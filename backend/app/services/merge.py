import json
import asyncio
from openai import AsyncOpenAI

from app.core.config import settings
from app.core.logger import get_logger
from app.models.schemas import ExtractionResult, MergedRoom, DetectedElement, ArchitecturalFeatures

from pathlib import Path

logger = get_logger("merge")

PROMPTS_DIR = Path(__file__).parent / "prompts"


def load_prompt(filename: str) -> str:
    file_path = PROMPTS_DIR / filename
    return file_path.read_text(encoding="utf-8")


MERGE_PHOTOS_TEMPLATE = load_prompt("MergePhotos.md")


class MergeService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.qwen_vl_api_key,
            base_url=settings.vllm_base_url.rsplit("/v1", 1)[0] if "/v1" in settings.vllm_base_url else settings.vllm_base_url,
        )
        self.model = settings.model_name

    async def merge_results(self, extractions: list[ExtractionResult]) -> MergedRoom:
        if not extractions:
            logger.info("Merge called with empty extractions list, returning empty MergedRoom")
            return MergedRoom(
                confirmed_elements=[],
                unconfirmed_elements=[],
                spatial_conflicts=[],
                architectural_features=ArchitecturalFeatures(),
            )

        all_jsons = "\n".join(
            f"--- Photo {i + 1} ---\n{ext.model_dump_json(indent=2)}"
            for i, ext in enumerate(extractions)
        )

        prompt = MERGE_PHOTOS_TEMPLATE
        prompt = prompt.replace("{n}", str(len(extractions)))
        prompt = prompt.replace("{all_photo_jsons}", all_jsons)

        logger.info(f"Merging {len(extractions)} extraction results (prompt size: {len(prompt)} chars)")
        raw = await self._call_llm(prompt)
        result = self._parse_merge(raw)
        logger.info(
            f"Merge complete: {len(result.confirmed_elements)} confirmed, "
            f"{len(result.unconfirmed_elements)} unconfirmed, "
            f"{len(result.spatial_conflicts)} conflicts"
        )
        return result

    async def _call_llm(self, prompt: str, max_retries: int = 3) -> str:
        for attempt in range(max_retries):
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt,
                        }
                    ],
                    temperature=0.0,
                    max_tokens=4096,
                )
                raw = response.choices[0].message.content
                logger.debug(f"Merge LLM response ({len(raw)} chars): {raw[:500]}{'...' if len(raw) > 500 else ''}")
                return raw
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"Merge LLM call failed after {max_retries} attempts: {type(e).__name__}: {e}")
                    raise
                logger.warning(f"Merge LLM call failed (attempt {attempt + 1}/{max_retries}): {type(e).__name__}, retrying...")
                await asyncio.sleep(2 ** attempt)

    def _parse_merge(self, raw: str) -> MergedRoom:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            import re

            match = re.search(r"\{[\s\S]*\}", raw)
            if match:
                data = json.loads(match.group())
                logger.warning(f"Merge JSON parse required regex fallback, matched {len(match.group())} chars")
            else:
                logger.error(f"Failed to parse merge JSON: {raw[:300]}")
                raise ValueError(f"Failed to parse merge JSON: {raw[:200]}")

        confirmed = [DetectedElement(**e) for e in data.get("confirmed_elements", [])]
        unconfirmed = [DetectedElement(**e) for e in data.get("unconfirmed_elements", [])]
        arch_data = data.get("architectural_features", {})

        return MergedRoom(
            confirmed_elements=confirmed,
            unconfirmed_elements=unconfirmed,
            spatial_conflicts=data.get("spatial_conflicts", []),
            architectural_features=ArchitecturalFeatures(
                doors=arch_data.get("doors", []),
                windows=arch_data.get("windows", []),
                visible_walls=arch_data.get("visible_walls", []),
            ),
        )


merge_service = MergeService()