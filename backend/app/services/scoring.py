import json
from typing import Optional

from app.core.prompts import load_prompt
from app.core.logger import get_logger, redact_session_id
from app.models.schemas import Dimensions
from app.services.llm import TextLLMService

logger = get_logger("scoring")

SCHOOL_PROMPTS = {
    "black_hat": "FengShuiScoring.md",
    "form": "FengShuiScoring-FormSchool.md",
    "three_door": "FengShuiScoring-ThreeDoorGate.md",
    "five_elements": "FengShuiScoring-FiveElements.md",
    "compass": "FengShuiScoring-Compass.md",
}


class ScoringService(TextLLMService):
    def _format_prompt(
        self,
        school: str,
        elements: list[dict],
        dimensions: Optional[Dimensions] = None,
        birth_date: Optional[str] = None,
        kua_number: Optional[int] = None,
        building_date: Optional[str] = None,
    ) -> str:
        prompt_file = SCHOOL_PROMPTS.get(school, "FengShuiScoring.md")
        prompt = load_prompt(prompt_file)

        dims_str = "not provided"
        if dimensions:
            dims_str = f"length: {dimensions.length}{dimensions.unit}, width: {dimensions.width}{dimensions.unit}"

        elements_json = json.dumps(elements, indent=2)

        prompt = prompt.replace("{dimensions}", dims_str)
        prompt = prompt.replace("{building_date}", building_date or "not provided")
        prompt = prompt.replace("{birth_date}", birth_date or "not provided")
        prompt = prompt.replace("{kua_number}", str(kua_number) if kua_number else "not provided")

        full_prompt = f"""{prompt}

## Detected Elements (from room analysis)

```json
{elements_json}
```

## Your Task

Analyze the detected elements using the {school.replace("_", " ").title()} scoring rubric above.
Return ONLY valid JSON matching the output schema specified in the prompt.
"""
        return full_prompt

    async def score(
        self,
        elements: list[dict],
        school: str = "black_hat",
        dimensions: Optional[Dimensions] = None,
        birth_date: Optional[str] = None,
        kua_number: Optional[int] = None,
        building_date: Optional[str] = None,
        max_retries: int = 3,
    ) -> dict:
        logger.info(f"Scoring room: school={school}, elements={len(elements)}, session={redact_session_id('scoring')}")

        prompt = self._format_prompt(school, elements, dimensions, birth_date, kua_number, building_date)

        for attempt in range(max_retries):
            try:
                raw = await self.call_text(prompt)
                result = self._parse_json_with_fallback(raw, context="scoring")
                logger.info(f"Scoring complete: total_score={result.get('total_score', 0)}, chi_flow={result.get('chi_flow', 'unknown')}")
                return result
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"Scoring failed after {max_retries} attempts: {type(e).__name__}: {e}")
                    raise
                logger.warning(f"Scoring failed (attempt {attempt + 1}/{max_retries}): {type(e).__name__}, retrying...")
                import asyncio
                await asyncio.sleep(2 ** attempt)


_scoring_service: Optional[ScoringService] = None


def get_scoring_service() -> ScoringService:
    global _scoring_service
    if _scoring_service is None:
        _scoring_service = ScoringService()
    return _scoring_service


def __getattr__(name: str):
    if name == "scoring_service":
        return get_scoring_service()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")