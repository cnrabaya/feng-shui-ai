import pytest
from unittest.mock import AsyncMock, patch

from app.models.schemas import Dimensions, RoomGrid
from app.services.layout import LayoutService


MOCK_GRID_RESPONSE = """{
  "cells": {
    "0,0": "bed", "0,1": "bed", "0,2": "empty", "0,3": "plant",
    "1,0": "empty", "1,1": "empty", "1,2": "rug", "1,3": "empty",
    "2,0": "sofa", "2,1": "sofa", "2,2": "coffee_table", "2,3": "lamp_floor",
    "3,0": "empty", "3,1": "empty", "3,2": "empty", "3,3": "bookshelf"
  },
  "grid_size": "4x4"
}"""

MOCK_GRID_WRAPPED = "Here is the layout:\n" + MOCK_GRID_RESPONSE + "\nDoes this look right?"


def make_mock_response(content: str):
    mock_choice = type("MockChoice", (), {
        "message": type("MockMessage", (), {"content": content})()
    })()
    return type("MockResponse", (), {"choices": [mock_choice]})()


@pytest.fixture
def layout_service():
    return LayoutService()


class TestLayoutService:
    @pytest.mark.asyncio
    async def test_generate_grid_returns_valid_room_grid(self, layout_service: LayoutService):
        mock_response = make_mock_response(MOCK_GRID_RESPONSE)

        with patch.object(layout_service.client, "chat", type("MockChat", (), {
            "completions": type("MockCompletions", (), {
                "create": AsyncMock(return_value=mock_response)
            })()
        })()):
            result = await layout_service.generate_grid(
                '{"elements": []}',
                Dimensions(length=4.5, width=3.5)
            )

        assert isinstance(result, RoomGrid)
        assert result.grid_size == "4x4"
        assert len(result.cells) == 16
        assert "0,0" in result.cells
        assert "3,3" in result.cells
        assert result.cells["0,0"] == "bed"
        assert result.cells["3,3"] == "bookshelf"
        assert result.cells["0,2"] == "empty"

    @pytest.mark.asyncio
    async def test_generate_grid_parse_fallback(self, layout_service: LayoutService):
        mock_response = make_mock_response(MOCK_GRID_WRAPPED)

        with patch.object(layout_service.client, "chat", type("MockChat", (), {
            "completions": type("MockCompletions", (), {
                "create": AsyncMock(return_value=mock_response)
            })()
        })()):
            result = await layout_service.generate_grid(
                '{"elements": []}',
                Dimensions(length=4.5, width=3.5)
            )

        assert isinstance(result, RoomGrid)
        assert len(result.cells) == 16
        assert result.cells["0,0"] == "bed"

    @pytest.mark.asyncio
    async def test_generate_grid_max_retries(self, layout_service: LayoutService):
        mock_fail = make_mock_response("not json")
        mock_success = make_mock_response(MOCK_GRID_RESPONSE)

        call_count = 0

        async def mock_create(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                return mock_fail
            return mock_success

        with patch.object(layout_service.client, "chat", type("MockChat", (), {
            "completions": type("MockCompletions", (), {
                "create": mock_create
            })()
        })()):
            result = await layout_service.generate_grid(
                '{"elements": []}',
                Dimensions(length=4.5, width=3.5)
            )

        assert call_count == 3
        assert isinstance(result, RoomGrid)
        assert result.cells["0,0"] == "bed"

    @pytest.mark.asyncio
    async def test_generate_grid_non_empty_uses_furniture_types(self, layout_service: LayoutService):
        mock_response = make_mock_response(MOCK_GRID_RESPONSE)

        with patch.object(layout_service.client, "chat", type("MockChat", (), {
            "completions": type("MockCompletions", (), {
                "create": AsyncMock(return_value=mock_response)
            })()
        })()):
            result = await layout_service.generate_grid(
                '{"elements": [{"id": "sofa_1", "type": "sofa"}]}',
                Dimensions(length=4.5, width=3.5)
            )

        valid_types = {"bed", "sofa", "armchair", "dining_table", "coffee_table",
                      "desk", "wardrobe", "dresser", "bookshelf", "tv_stand",
                      "plant", "lamp_floor", "lamp_table", "lamp_ceiling",
                      "mirror", "rug", "curtains", "artwork", "door", "window", "empty"}
        for key, value in result.cells.items():
            assert value in valid_types, f"Cell {key} has invalid type: {value}"

    @pytest.mark.asyncio
    async def test_generate_grid_cells_keys_cover_all_16_positions(self, layout_service: LayoutService):
        mock_response = make_mock_response(MOCK_GRID_RESPONSE)

        with patch.object(layout_service.client, "chat", type("MockChat", (), {
            "completions": type("MockCompletions", (), {
                "create": AsyncMock(return_value=mock_response)
            })()
        })()):
            result = await layout_service.generate_grid("{}", Dimensions(length=4.5, width=3.5))

        expected_keys = {f"{r},{c}" for r in range(4) for c in range(4)}
        assert set(result.cells.keys()) == expected_keys

    @pytest.mark.asyncio
    async def test_generate_grid_uses_correct_dimensions_in_prompt(self, layout_service: LayoutService):
        captured_messages = None

        original_create = layout_service.client.chat.completions.create

        async def capture_create(*args, **kwargs):
            nonlocal captured_messages
            captured_messages = kwargs.get("messages") or (args[0] if args else None)
            return make_mock_response(MOCK_GRID_RESPONSE)

        with patch.object(layout_service.client.chat.completions, "create", capture_create):
            await layout_service.generate_grid(
                '{"elements": []}',
                Dimensions(length=6.0, width=4.0)
            )

        prompt_text = captured_messages[0]["content"]
        assert "6.0" in prompt_text
        assert "4.0" in prompt_text
        assert "6.0m x 4.0m" in prompt_text