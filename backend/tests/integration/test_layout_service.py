import pytest
from unittest.mock import AsyncMock, patch

from app.models.schemas import Dimensions, RoomGrid
from app.services.layout import LayoutService


MOCK_GRID_SIZE = "4x4"
MOCK_GRID_N = int(MOCK_GRID_SIZE.split("x")[0])


def _make_grid_response(grid_size: str, n: int) -> str:
    cells = {f"{r},{c}": "empty" for r in range(n) for c in range(n)}
    if n >= 3:
        cells["0,0"] = "bed"
        cells["0,1"] = "bed"
        cells["2,0"] = "sofa"
        cells["2,1"] = "sofa"
        cells["2,2"] = "coffee_table"
    if n >= 4:
        cells["3,3"] = "bookshelf"
    import json
    return json.dumps({"cells": cells, "grid_size": grid_size})


MOCK_GRID_RESPONSE = _make_grid_response(MOCK_GRID_SIZE, MOCK_GRID_N)
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
                Dimensions(length=4.5, width=3.5),
                grid_size=MOCK_GRID_SIZE,
            )

        assert isinstance(result, RoomGrid)
        assert result.grid_size == MOCK_GRID_SIZE
        assert result.scale_note == "Each cell represents approximately 1/16 of the room. 0,0 = top-left (north-west corner)."
        assert len(result.cells) == MOCK_GRID_N * MOCK_GRID_N
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
                Dimensions(length=4.5, width=3.5),
                grid_size=MOCK_GRID_SIZE,
            )

        assert isinstance(result, RoomGrid)
        assert len(result.cells) == MOCK_GRID_N * MOCK_GRID_N
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
                Dimensions(length=4.5, width=3.5),
                grid_size=MOCK_GRID_SIZE,
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
                Dimensions(length=4.5, width=3.5),
                grid_size=MOCK_GRID_SIZE,
            )

        valid_types = {"bed", "sofa", "armchair", "dining_table", "coffee_table",
                      "desk", "wardrobe", "dresser", "bookshelf", "tv_stand",
                      "plant", "lamp_floor", "lamp_table", "lamp_ceiling",
                      "mirror", "rug", "curtains", "artwork", "door", "window", "empty"}
        for key, value in result.cells.items():
            assert value in valid_types, f"Cell {key} has invalid type: {value}"

    @pytest.mark.asyncio
    async def test_generate_grid_cells_keys_cover_all_NxN_positions(self, layout_service: LayoutService):
        mock_response = make_mock_response(MOCK_GRID_RESPONSE)

        with patch.object(layout_service.client, "chat", type("MockChat", (), {
            "completions": type("MockCompletions", (), {
                "create": AsyncMock(return_value=mock_response)
            })()
        })()):
            result = await layout_service.generate_grid("{}", Dimensions(length=4.5, width=3.5), grid_size=MOCK_GRID_SIZE)

        expected_keys = {f"{r},{c}" for r in range(MOCK_GRID_N) for c in range(MOCK_GRID_N)}
        assert set(result.cells.keys()) == expected_keys

    @pytest.mark.asyncio
    async def test_generate_grid_uses_correct_dimensions_in_prompt(self, layout_service: LayoutService):
        captured_messages = None

        async def capture_create(*args, **kwargs):
            nonlocal captured_messages
            captured_messages = kwargs.get("messages") or (args[0] if args else None)
            return make_mock_response(MOCK_GRID_RESPONSE)

        with patch.object(layout_service.client.chat.completions, "create", capture_create):
            await layout_service.generate_grid(
                '{"elements": []}',
                Dimensions(length=6.0, width=4.0),
                grid_size=MOCK_GRID_SIZE,
            )

        prompt_text = captured_messages[0]["content"]
        assert "6.0" in prompt_text
        assert "4.0" in prompt_text
        assert "6.0m x 4.0m" in prompt_text

    @pytest.mark.asyncio
    async def test_generate_grid_3x3(self, layout_service: LayoutService):
        grid_size = "3x3"
        n = 3
        mock_response = make_mock_response(_make_grid_response(grid_size, n))

        with patch.object(layout_service.client, "chat", type("MockChat", (), {
            "completions": type("MockCompletions", (), {
                "create": AsyncMock(return_value=mock_response)
            })()
        })()):
            result = await layout_service.generate_grid(
                '{"elements": []}',
                Dimensions(length=4.5, width=3.5),
                grid_size=grid_size,
            )

        assert isinstance(result, RoomGrid)
        assert result.grid_size == "3x3"
        assert result.scale_note == "Each cell represents approximately 1/9 of the room. 0,0 = top-left (north-west corner)."
        assert len(result.cells) == 9
        expected_keys = {f"{r},{c}" for r in range(3) for c in range(3)}
        assert set(result.cells.keys()) == expected_keys

    @pytest.mark.asyncio
    async def test_generate_grid_wrong_cell_count_raises(self, layout_service: LayoutService):
        bad_response = make_mock_response('{"cells": {"0,0": "bed", "0,1": "empty"}, "grid_size": "3x3"}')

        with patch.object(layout_service.client, "chat", type("MockChat", (), {
            "completions": type("MockCompletions", (), {
                "create": AsyncMock(return_value=bad_response)
            })()
        })()):
            with pytest.raises(ValueError, match="requires 9( cells)?"):
                await layout_service.generate_grid(
                    '{"elements": []}',
                    Dimensions(length=4.5, width=3.5),
                    grid_size="3x3",
                )

    @pytest.mark.asyncio
    async def test_generate_grid_prompt_contains_grid_size_and_scale_note(self, layout_service: LayoutService):
        captured_messages = None
        test_grid_size = "5x5"
        test_n = 5
        mock_response_content = _make_grid_response(test_grid_size, test_n)

        async def capture_create(*args, **kwargs):
            nonlocal captured_messages
            captured_messages = kwargs.get("messages") or (args[0] if args else None)
            return make_mock_response(mock_response_content)

        with patch.object(layout_service.client.chat.completions, "create", capture_create):
            await layout_service.generate_grid(
                '{"elements": []}',
                Dimensions(length=6.0, width=4.0),
                grid_size=test_grid_size,
            )

        prompt_text = captured_messages[0]["content"]
        assert '"grid_size": "5x5"' in prompt_text
        assert "1/25" in prompt_text
        assert '"5x5"' in prompt_text
        assert "5x5 grid" in prompt_text or "5x5" in prompt_text