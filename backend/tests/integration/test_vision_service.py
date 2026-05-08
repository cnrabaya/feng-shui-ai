import pytest
from unittest.mock import AsyncMock, patch

from app.models.schemas import ExtractionResult, MultiImageData
from app.services.vision import VisionService


MOCK_EXTRACTION_RESPONSE = """{
  "elements": [
    {"id": "sofa_1", "type": "sofa", "position_relative_to_camera": "center", "wall_association": "south wall", "partially_visible": false, "confidence": "high"},
    {"id": "plant_1", "type": "plant", "position_relative_to_camera": "right", "wall_association": "east wall", "partially_visible": false, "confidence": "high"}
  ],
  "architectural_features": {
    "doors": [{"location": "north wall", "facing": "south"}],
    "windows": [{"location": "east wall", "count": 1}],
    "visible_walls": ["north", "east", "south"]
  }
}"""


def make_mock_response(content: str):
    mock_choice = type("MockChoice", (), {
        "message": type("MockMessage", (), {"content": content})()
    })()
    return type("MockResponse", (), {"choices": [mock_choice]})()


@pytest.fixture
def vision_service():
    return VisionService()


class TestVisionServiceSingle:
    @pytest.mark.asyncio
    async def test_extract_elements_returns_valid_result(self, vision_service: VisionService):
        mock_response = make_mock_response(MOCK_EXTRACTION_RESPONSE)

        with patch.object(vision_service.client, "chat", type("MockChat", (), {"completions": type("MockCompletions", (), {"create": AsyncMock(return_value=mock_response)})()})()):
            result = await vision_service.extract_elements("fake_base64_image_data")

        assert isinstance(result, ExtractionResult)
        assert len(result.elements) == 2
        assert result.elements[0].type == "sofa"
        assert result.elements[0].confidence == "high"
        assert len(result.architectural_features.doors) == 1
        assert len(result.architectural_features.windows) == 1

    @pytest.mark.asyncio
    async def test_extract_elements_with_direction(self, vision_service: VisionService):
        mock_response = make_mock_response(MOCK_EXTRACTION_RESPONSE)

        with patch.object(vision_service.client, "chat", type("MockChat", (), {"completions": type("MockCompletions", (), {"create": AsyncMock(return_value=mock_response)})()})()):
            result = await vision_service.extract_elements("fake_base64", direction="north")

        assert isinstance(result, ExtractionResult)
        assert len(result.elements) == 2

    @pytest.mark.asyncio
    async def test_extract_elements_parse_fallback(self, vision_service: VisionService):
        raw = "NOT JSON\n{\"elements\": [{\"id\": \"lamp_1\", \"type\": \"lamp\", \"position_relative_to_camera\": \"center\", \"wall_association\": null, \"partially_visible\": false, \"confidence\": \"medium\"}], \"architectural_features\": {}}\nMORE TEXT"
        mock_response = make_mock_response(raw)

        with patch.object(vision_service.client, "chat", type("MockChat", (), {"completions": type("MockCompletions", (), {"create": AsyncMock(return_value=mock_response)})()})()):
            result = await vision_service.extract_elements("fake_base64")

        assert len(result.elements) == 1
        assert result.elements[0].id == "lamp_1"

    @pytest.mark.asyncio
    async def test_extract_elements_parse_error(self, vision_service: VisionService):
        mock_response = make_mock_response("this is not json at all")

        with patch.object(vision_service.client, "chat", type("MockChat", (), {"completions": type("MockCompletions", (), {"create": AsyncMock(return_value=mock_response)})()})()):
            with pytest.raises(ValueError):
                await vision_service.extract_elements("fake_base64")

    @pytest.mark.asyncio
    async def test_extract_elements_empty_response(self, vision_service: VisionService):
        mock_response = make_mock_response('{"elements": [], "architectural_features": {}}')

        with patch.object(vision_service.client, "chat", type("MockChat", (), {"completions": type("MockCompletions", (), {"create": AsyncMock(return_value=mock_response)})()})()):
            result = await vision_service.extract_elements("fake_base64")

        assert len(result.elements) == 0


class TestVisionServiceBatch:
    @pytest.mark.asyncio
    async def test_extract_elements_batch_returns_results(self, vision_service: VisionService):
        mock_response = make_mock_response(MOCK_EXTRACTION_RESPONSE)

        images = [
            MultiImageData(image="fake_base64_1", direction="north"),
            MultiImageData(image="fake_base64_2", direction="south"),
        ]

        with patch.object(vision_service.client, "chat", type("MockChat", (), {"completions": type("MockCompletions", (), {"create": AsyncMock(return_value=mock_response)})()})()):
            results = await vision_service.extract_elements_batch(images)

        assert len(results) == 2
        for result in results:
            assert isinstance(result, ExtractionResult)

    @pytest.mark.asyncio
    async def test_extract_elements_batch_single_item(self, vision_service: VisionService):
        mock_response = make_mock_response(MOCK_EXTRACTION_RESPONSE)
        images = [MultiImageData(image="fake_base64", direction="not_sure")]

        with patch.object(vision_service.client, "chat", type("MockChat", (), {"completions": type("MockCompletions", (), {"create": AsyncMock(return_value=mock_response)})()})()):
            results = await vision_service.extract_elements_batch(images)

        assert len(results) == 1
        assert len(results[0].elements) == 2