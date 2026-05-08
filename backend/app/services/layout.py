import asyncio

from app.core.prompts import load_prompt
from app.core.logger import get_logger
from app.models.schemas import RoomGrid, Dimensions
from app.services.llm import TextLLMService

logger = get_logger("layout")

ROOM_LAYOUT_TEMPLATE = load_prompt("RoomLayout.md")
ELEMENT_NAMING_SCHEME = load_prompt("ElementNamingScheme.md")

_layout_service: "LayoutService | None" = None


class LayoutService(TextLLMService):
    def __init__(self):
        super().__init__(max_tokens=1024)

    def _format_layout_prompt(self, extraction_json: str, dimensions: Dimensions) -> str:
        prompt = ROOM_LAYOUT_TEMPLATE + ELEMENT_NAMING_SCHEME
        prompt = prompt.replace("{extraction_json}", extraction_json)
        prompt = prompt.replace("{room_length}", str(dimensions.length))
        prompt = prompt.replace("{room_width}", str(dimensions.width))
        return prompt

    async def generate_grid(self, extraction_json: str, dimensions: Dimensions, max_retries: int = 3) -> RoomGrid:
        prompt = self._format_layout_prompt(extraction_json, dimensions)
        logger.debug(f"Layout prompt ({len(prompt)} chars)")

        messages = self._build_text_messages(prompt)

        for attempt in range(max_retries):
            try:
                raw = await self._call_llm(messages, max_tokens=1024)

                data = self._parse_json_with_fallback(raw, "layout")
                cells = data.get("cells", {})
                if not cells:
                    raise ValueError(f"Layout response missing 'cells' field: {raw[:200]}")

                return RoomGrid(cells=cells)

            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"Layout generation failed after {max_retries} attempts: {type(e).__name__}: {e}")
                    raise
                logger.warning(f"Layout generation failed (attempt {attempt + 1}/{max_retries}): {type(e).__name__}, retrying...")
                await asyncio.sleep(2 ** attempt)


def get_layout_service() -> LayoutService:
    global _layout_service
    if _layout_service is None:
        _layout_service = LayoutService()
    return _layout_service


def __getattr__(name: str):
    if name == "layout_service":
        return get_layout_service()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")