import json
import asyncio
from openai import AsyncOpenAI
from typing import Optional, Any

from app.core.config import settings
from app.core.logger import get_logger, redact_session_id
from app.core.prompts import load_prompt
from app.models.schemas import Dimensions

logger = get_logger("scoring")

SCHOOL_PROMPTS = {
    "black_hat": "FengShuiScoring.md",
    "form": "FengShuiScoring-FormSchool.md",
    "three_door": "FengShuiScoring-ThreeDoorGate.md",
    "five_elements": "FengShuiScoring-FiveElements.md",
    "compass": "FengShuiScoring-Compass.md",
}


class ScoringService:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.api_key,
            base_url=settings.vllm_base_url,
        )
        self.model = settings.model_name

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

    async def _call_qwen(self, prompt: str, max_retries: int = 3) -> str:
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
                logger.debug(f"Scoring AI response ({len(raw)} chars): {raw[:500]}{'...' if len(raw) > 500 else ''}")
                return raw
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"Scoring Qwen-VL call failed after {max_retries} attempts: {type(e).__name__}: {e}")
                    raise
                logger.warning(f"Scoring Qwen-VL call failed (attempt {attempt + 1}/{max_retries}): {type(e).__name__}, retrying...")
                await asyncio.sleep(2 ** attempt)

    def _parse_score_response(self, raw: str) -> dict:
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            import re
            match = re.search(r"\{[\s\S]*\}", raw)
            if match:
                data = json.loads(match.group())
                logger.warning(f"Scoring JSON parse required regex fallback, matched {len(match.group())} chars")
            else:
                logger.error(f"Failed to parse scoring JSON from Qwen-VL response: {raw[:300]}")
                raise ValueError(f"Failed to parse scoring JSON: {raw[:200]}")
        return data

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
                raw = await self._call_qwen(prompt)
                result = self._parse_score_response(raw)
                logger.info(f"Scoring complete: total_score={result.get('total_score', 0)}, chi_flow={result.get('chi_flow', 'unknown')}")
                return result
            except Exception as e:
                if attempt == max_retries - 1:
                    logger.error(f"Scoring failed after {max_retries} attempts: {type(e).__name__}: {e}")
                    raise
                logger.warning(f"Scoring failed (attempt {attempt + 1}/{max_retries}): {type(e).__name__}, retrying...")
                await asyncio.sleep(2 ** attempt)


scoring_service = ScoringService()