import asyncio

from app.core.prompts import load_prompt
from app.core.logger import get_logger, redact_image
from app.models.schemas import (
    ExtractionResult,
    DetectedElement,
    ArchitecturalFeatures,
    MultiImageData,
    Dimensions,
)
from app.services.llm import VisionLLMService

logger = get_logger("vision")

ELEMENT_EXTRACTION_TEMPLATE = load_prompt("ElementExtraction.md")
ELEMENT_NAMING_SCHEME = load_prompt("ElementNamingScheme.md")

_vision_service: "VisionService | None" = None


class VisionService(VisionLLMService):
    def __init__(self):
        super().__init__(max_tokens=4096)

    def _format_element_prompt(self, direction: str | None = None, dimensions: Dimensions | None = None) -> str:
        prompt = ELEMENT_EXTRACTION_TEMPLATE + ELEMENT_NAMING_SCHEME
        if dimensions:
            dim_line = f"Room dimensions: {dimensions.length}m x {dimensions.width}m. Use this scale to estimate furniture size."
            prompt = prompt.replace("Room dimensions: {room_dimensions}", dim_line)
        else:
            prompt = prompt.replace("Room dimensions: {room_dimensions}\n", "")
        if direction and direction != "not_sure":
            prompt = prompt.replace("{direction}", direction)
        else:
            prompt = prompt.replace("You are looking at the room from the direction: {direction}\n\n", "")
        return prompt

    async def extract_elements(
        self,
        image_base64: str,
        direction: str | None = None,
        dimensions: Dimensions | None = None,
        return_raw: bool = False,
    ) -> ExtractionResult | tuple[ExtractionResult, str]:
        prompt = self._format_element_prompt(direction, dimensions)
        logger.info(f"Extracting elements (direction={direction or 'unknown'}, image={redact_image(image_base64[:100])})")
        raw = await self.call_vision(image_base64, prompt)
        result = self._parse_extraction(raw)
        logger.info(
            f"Extraction complete: {len(result.elements)} elements, "
            f"{len(result.architectural_features.doors)} doors, "
            f"{len(result.architectural_features.windows)} windows"
        )
        if return_raw:
            return result, raw
        return result

    async def extract_elements_batch(
        self,
        images: list[MultiImageData],
        max_concurrency: int = 3,
        dimensions: Dimensions | None = None,
        return_raw: bool = False,
    ) -> list[ExtractionResult | tuple[ExtractionResult, str]]:
        logger.info(f"Batch extraction: {len(images)} image(s), max_concurrency={max_concurrency}")
        semaphore = asyncio.Semaphore(max_concurrency)

        async def extract_one(img_data: MultiImageData) -> ExtractionResult | tuple[ExtractionResult, str]:
            async with semaphore:
                return await self.extract_elements(
                    img_data.image, img_data.direction, dimensions=dimensions, return_raw=return_raw
                )

        tasks = [extract_one(img) for img in images]
        results = await asyncio.gather(*tasks)
        total_elements = sum(len(r[0].elements) if isinstance(r, tuple) else len(r.elements) for r in results)
        logger.info(f"Batch extraction complete: {len(results)} photos, {total_elements} total elements")
        return results

    def _parse_extraction(self, raw: str) -> ExtractionResult:
        data = self._parse_json_with_fallback(raw, "extraction")

        elements = [DetectedElement(**e) for e in data.get("elements", [])]
        arch_data = data.get("architectural_features", {})

        return ExtractionResult(
            elements=elements,
            architectural_features=ArchitecturalFeatures(
                doors=self._normalize_to_string_list(arch_data.get("doors", [])),
                windows=self._normalize_to_string_list(arch_data.get("windows", [])),
                visible_walls=arch_data.get("visible_walls", []),
            ),
        )


def get_vision_service() -> VisionService:
    global _vision_service
    if _vision_service is None:
        _vision_service = VisionService()
    return _vision_service


def __getattr__(name: str):
    if name == "vision_service":
        return get_vision_service()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")