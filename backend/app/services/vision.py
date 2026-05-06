import json
import asyncio
from openai import AsyncOpenAI

from app.core.config import settings
from app.core.logger import get_logger, redact_image
from app.models.schemas import (
    ExtractionResult,
    DetectedElement,
    ArchitecturalFeatures,
    MultiImageData,
)

from pathlib import Path

logger = get_logger("vision")

PROMPTS_DIR = Path(__file__).parent / "prompts"


def load_prompt(filename: str) -> str:
    file_path = PROMPTS_DIR / filename
    return file_path.read_text(encoding="utf-8")


ELEMENT_EXTRACTION_TEMPLATE = load_prompt("ElementExtraction.md")
ELEMENT_NAMING_SCHEME = load_prompt("ElementNamingScheme.md")


class VisionService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.qwen_vl_api_key,
            base_url=settings.vllm_base_url.rsplit("/v1", 1)[0] if "/v1" in settings.vllm_base_url else settings.vllm_base_url,
        )
        self.model = settings.model_name

    def _format_element_prompt(self, direction: str | None = None) -> str:
        prompt = ELEMENT_EXTRACTION_TEMPLATE + ELEMENT_NAMING_SCHEME
        if direction and direction != "not_sure":
            prompt = prompt.replace("{direction}", direction)
        else:
            prompt = prompt.replace("You are looking at the room from the direction: {direction}\n\n", "")
        return prompt

    async def _call_qwen(self, image_base64: str, prompt: str, max_retries: int = 3) -> str:
        for attempt in range(max_retries):
            try:
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"},
                                },
                            ],
                        }
                    ],
                    temperature=0.0,
                    max_tokens=4096,
                )
                raw = response.choices[0].message.content
                logger.debug(f"AI response ({len(raw)} chars): {raw[:500]}{'...' if len(raw) > 500 else ''}")
                return raw
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"Qwen-VL call failed after {max_retries} attempts: {type(e).__name__}: {e}")
                    raise
                logger.warning(f"Qwen-VL call failed (attempt {attempt + 1}/{max_retries}): {type(e).__name__}, retrying...")
                await asyncio.sleep(2 ** attempt)

    async def extract_elements(self, image_base64: str, direction: str | None = None) -> ExtractionResult:
        prompt = self._format_element_prompt(direction)
        logger.info(f"Extracting elements (direction={direction or 'unknown'}, image={redact_image(image_base64[:100])})")
        raw = await self._call_qwen(image_base64, prompt)
        result = self._parse_extraction(raw)
        logger.info(f"Extraction complete: {len(result.elements)} elements, {len(result.architectural_features.doors)} doors, {len(result.architectural_features.windows)} windows")
        return result

    async def extract_elements_batch(
        self, images: list[MultiImageData], max_concurrency: int = 3
    ) -> list[ExtractionResult]:
        logger.info(f"Batch extraction: {len(images)} image(s), max_concurrency={max_concurrency}")
        semaphore = asyncio.Semaphore(max_concurrency)

        async def extract_one(img_data: MultiImageData) -> ExtractionResult:
            async with semaphore:
                result = await self.extract_elements(img_data.image, img_data.direction)
                return result

        tasks = [extract_one(img) for img in images]
        results = await asyncio.gather(*tasks)
        total_elements = sum(len(r.elements) for r in results)
        logger.info(f"Batch extraction complete: {len(results)} photos, {total_elements} total elements")
        return results

    def _parse_extraction(self, raw: str) -> ExtractionResult:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            import re

            match = re.search(r"\{[\s\S]*\}", raw)
            if match:
                data = json.loads(match.group())
                logger.warning(f"JSON parse required regex fallback, matched {len(match.group())} chars")
            else:
                logger.error(f"Failed to parse JSON from Qwen-VL response: {raw[:300]}")
                raise ValueError(f"Failed to parse JSON from Qwen-VL response: {raw[:200]}")

        elements = [DetectedElement(**e) for e in data.get("elements", [])]
        arch_data = data.get("architectural_features", {})
        return ExtractionResult(
            elements=elements,
            architectural_features=ArchitecturalFeatures(
                doors=arch_data.get("doors", []),
                windows=arch_data.get("windows", []),
                visible_walls=arch_data.get("visible_walls", []),
            ),
        )


vision_service = VisionService()