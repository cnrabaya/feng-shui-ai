from app.core.prompts import load_prompt
from app.core.logger import get_logger
from app.models.schemas import ExtractionResult, MergedRoom, DetectedElement, ArchitecturalFeatures
from app.services.llm import TextLLMService

logger = get_logger("merge")

MERGE_PHOTOS_TEMPLATE = load_prompt("MergePhotos.md")

_merge_service: "MergeService | None" = None


class MergeService(TextLLMService):
    def __init__(self):
        super().__init__(max_tokens=4096)

    async def merge_results(self, extractions: list[ExtractionResult | tuple[ExtractionResult, str]]) -> MergedRoom:
        if not extractions:
            logger.info("Merge called with empty extractions list, returning empty MergedRoom")
            return MergedRoom(
                confirmed_elements=[],
                unconfirmed_elements=[],
                spatial_conflicts=[],
                architectural_features=ArchitecturalFeatures(),
            )

        parsed = [e[0] if isinstance(e, tuple) else e for e in extractions]
        all_jsons = "\n".join(
            f"--- Photo {i + 1} ---\n{ext.model_dump_json(indent=2)}"
            for i, ext in enumerate(parsed)
        )

        prompt = MERGE_PHOTOS_TEMPLATE
        prompt = prompt.replace("{n}", str(len(extractions)))
        prompt = prompt.replace("{all_photo_jsons}", all_jsons)

        logger.info(f"Merging {len(extractions)} extraction results (prompt size: {len(prompt)} chars)")
        raw = await self.call_text(prompt)
        result = self._parse_merge(raw)
        logger.info(
            f"Merge complete: {len(result.confirmed_elements)} confirmed, "
            f"{len(result.unconfirmed_elements)} unconfirmed, "
            f"{len(result.spatial_conflicts)} conflicts"
        )
        return result

    def _parse_merge(self, raw: str) -> MergedRoom:
        data = self._parse_json_with_fallback(raw, "merge")

        confirmed = [DetectedElement(**e) for e in data.get("confirmed_elements", [])]
        unconfirmed = [DetectedElement(**e) for e in data.get("unconfirmed_elements", [])]
        arch_data = data.get("architectural_features", {})

        return MergedRoom(
            confirmed_elements=confirmed,
            unconfirmed_elements=unconfirmed,
            spatial_conflicts=data.get("spatial_conflicts", []),
            architectural_features=ArchitecturalFeatures(
                doors=self._normalize_to_string_list(arch_data.get("doors", [])),
                windows=self._normalize_to_string_list(arch_data.get("windows", [])),
                visible_walls=arch_data.get("visible_walls", []),
            ),
        )


def get_merge_service() -> MergeService:
    global _merge_service
    if _merge_service is None:
        _merge_service = MergeService()
    return _merge_service


def __getattr__(name: str):
    if name == "merge_service":
        return get_merge_service()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")