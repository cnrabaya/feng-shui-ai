import pytest
from unittest.mock import AsyncMock, patch

from app.models.schemas import ExtractionResult, DetectedElement, ArchitecturalFeatures, MergedRoom
from app.services.merge import MergeService


MOCK_MERGE_RESPONSE = """{
  "confirmed_elements": [
    {"id": "sofa_1", "type": "sofa", "position_relative_to_camera": "center", "wall_association": "south wall", "partially_visible": false, "confidence": "high"},
    {"id": "plant_1", "type": "plant", "position_relative_to_camera": "right", "wall_association": "east wall", "partially_visible": false, "confidence": "high"}
  ],
  "unconfirmed_elements": [
    {"id": "lamp_1", "type": "lamp", "position_relative_to_camera": "left", "wall_association": "west wall", "partially_visible": true, "confidence": "low"}
  ],
  "architectural_features": {
    "doors": [{"location": "north wall"}],
    "windows": [{"location": "east wall", "count": 1}],
    "visible_walls": ["north", "east", "south"]
  },
  "spatial_conflicts": []
}"""


def make_mock_response(content: str):
    mock_choice = type("MockChoice", (), {
        "message": type("MockMessage", (), {"content": content})()
    })()
    return type("MockResponse", (), {"choices": [mock_choice]})()


def make_extraction(type_: str, id_: str) -> ExtractionResult:
    return ExtractionResult(
        elements=[DetectedElement(id=id_, type=type_, position_relative_to_camera="center")],
        architectural_features=ArchitecturalFeatures(),
    )


@pytest.fixture
def merge_service():
    return MergeService()


class TestMergeService:
    @pytest.mark.asyncio
    async def test_merge_two_photos_confirms_duplicates(self, merge_service: MergeService):
        mock_response = make_mock_response(MOCK_MERGE_RESPONSE)
        extraction1 = make_extraction("sofa", "sofa_1")
        extraction2 = make_extraction("sofa", "sofa_1")

        with patch.object(merge_service.client, "chat", type("MockChat", (), {"completions": type("MockCompletions", (), {"create": AsyncMock(return_value=mock_response)})()})()):
            result = await merge_service.merge_results([extraction1, extraction2])

        assert isinstance(result, MergedRoom)
        assert len(result.confirmed_elements) == 2
        assert len(result.unconfirmed_elements) == 1
        assert len(result.spatial_conflicts) == 0

    @pytest.mark.asyncio
    async def test_merge_zero_extractions_returns_empty(self, merge_service: MergeService):
        result = await merge_service.merge_results([])
        assert isinstance(result, MergedRoom)
        assert len(result.confirmed_elements) == 0
        assert len(result.unconfirmed_elements) == 0

    @pytest.mark.asyncio
    async def test_merge_parse_fallback(self, merge_service: MergeService):
        raw = "NOT JSON\n" + MOCK_MERGE_RESPONSE + "\nMORE TEXT"
        mock_response = make_mock_response(raw)
        extraction = make_extraction("sofa", "sofa_1")

        with patch.object(merge_service.client, "chat", type("MockChat", (), {"completions": type("MockCompletions", (), {"create": AsyncMock(return_value=mock_response)})()})()):
            result = await merge_service.merge_results([extraction])

        assert len(result.confirmed_elements) == 2

    @pytest.mark.asyncio
    async def test_merge_parse_error(self, merge_service: MergeService):
        mock_response = make_mock_response("not valid json at all")
        extraction = make_extraction("sofa", "sofa_1")

        with patch.object(merge_service.client, "chat", type("MockChat", (), {"completions": type("MockCompletions", (), {"create": AsyncMock(return_value=mock_response)})()})()):
            with pytest.raises(ValueError, match="Failed to parse merge JSON"):
                await merge_service.merge_results([extraction])

    @pytest.mark.asyncio
    async def test_merge_includes_architectural_features(self, merge_service: MergeService):
        mock_response = make_mock_response(MOCK_MERGE_RESPONSE)
        extraction = make_extraction("sofa", "sofa_1")

        with patch.object(merge_service.client, "chat", type("MockChat", (), {"completions": type("MockCompletions", (), {"create": AsyncMock(return_value=mock_response)})()})()):
            result = await merge_service.merge_results([extraction])

        assert len(result.architectural_features.doors) == 1
        assert len(result.architectural_features.windows) == 1