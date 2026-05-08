import asyncio
import json

from app.core.prompts import load_prompt
from app.core.logger import get_logger
from app.models.schemas import RoomGrid, Dimensions
from app.services.llm import TextLLMService

logger = get_logger("layout")

ROOM_LAYOUT_TEMPLATE = load_prompt("RoomLayout.md")
ELEMENT_NAMING_SCHEME = load_prompt("ElementNamingScheme.md")

_layout_service: "LayoutService | None" = None


def _build_cells_json(grid_size: str) -> str:
    n = int(grid_size.split("x")[0])
    cells = {f"{r},{c}": "furniture_type or empty" for r in range(n) for c in range(n)}
    return json.dumps({"cells": cells, "grid_size": grid_size}, indent=2)


class LayoutService(TextLLMService):
    def __init__(self):
        super().__init__(max_tokens=1024)

    def _parse_grid_size(self, grid_size: str) -> int:
        try:
            n = int(grid_size.split("x")[0])
            if not 1 <= n <= 10:
                raise ValueError(f"grid_size must be 'NxN' with N in 1..10, got {grid_size!r}")
            return n
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid grid_size {grid_size!r}: expected 'NxN' with N in 1..10") from e

    def _format_layout_prompt(
        self,
        extraction_json: str,
        dimensions: Dimensions,
        grid_size: str = "4x4",
    ) -> tuple[str, str]:
        n = self._parse_grid_size(grid_size)
        total_cells = n * n
        scale_note = (
            f"Each cell represents approximately 1/{total_cells} of the room. "
            f"0,0 = top-left (north-west corner)."
        )
        cells_json = _build_cells_json(grid_size)

        prompt = ROOM_LAYOUT_TEMPLATE + ELEMENT_NAMING_SCHEME
        prompt = prompt.replace("{extraction_json}", extraction_json)
        prompt = prompt.replace("{room_length}", str(dimensions.length))
        prompt = prompt.replace("{room_width}", str(dimensions.width))
        prompt = prompt.replace("{grid_size}", grid_size)
        prompt = prompt.replace("{N}", str(n))
        prompt = prompt.replace("{scale_note}", scale_note)
        prompt = prompt.replace("{cells_json}", cells_json)
        return prompt, scale_note

    async def generate_grid(
        self,
        extraction_json: str,
        dimensions: Dimensions,
        grid_size: str = "4x4",
        max_retries: int = 3,
    ) -> RoomGrid:
        n = self._parse_grid_size(grid_size)
        expected_cell_count = n * n

        prompt, scale_note = self._format_layout_prompt(extraction_json, dimensions, grid_size)
        logger.debug(f"Layout prompt ({len(prompt)} chars), grid_size={grid_size}, N={n}")

        messages = self._build_text_messages(prompt)

        for attempt in range(max_retries):
            try:
                raw = await self._call_llm(messages, max_tokens=1024)

                data = self._parse_json_with_fallback(raw, "layout")
                cells = data.get("cells", {})
                if not cells:
                    raise ValueError(f"Layout response missing 'cells' field: {raw[:200]}")

                actual_count = len(cells)
                if actual_count != expected_cell_count:
                    raise ValueError(
                        f"Layout returned {actual_count} cells but {grid_size} requires {expected_cell_count}: {raw[:200]}"
                    )

                return RoomGrid(cells=cells, grid_size=grid_size, scale_note=scale_note)

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