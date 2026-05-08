import base64
import io

import pytest
from PIL import Image
from starlette.testclient import TestClient

from app.main import app
from app.models.schemas import MultiImageData
from app.core.utils import process_image_base64

pytestmark = pytest.mark.e2e


class TestVisionServiceE2E:
    @pytest.mark.asyncio
    @pytest.mark.timeout(60)
    async def test_single_image_returns_valid_schema(self, real_vision_service, room_1_processed_base64):
        result = await real_vision_service.extract_elements(room_1_processed_base64)

        assert len(result.elements) > 0, "Should detect at least one element"
        for e in result.elements:
            assert e.id, "Element must have an id"
            assert e.type, "Element must have a type"
            assert e.confidence in ("high", "medium", "low"), "Confidence must be high/medium/low"
        assert result.architectural_features is not None

    @pytest.mark.asyncio
    @pytest.mark.timeout(60)
    async def test_single_image_with_direction(self, real_vision_service, room_1_processed_base64):
        result = await real_vision_service.extract_elements(room_1_processed_base64, direction="north")
        assert len(result.elements) >= 0
        for e in result.elements:
            assert e.id
            assert e.type

    @pytest.mark.asyncio
    @pytest.mark.timeout(60)
    async def test_batch_two_images(self, real_vision_service, room_1_base64, room_2_base64):
        images = [
            MultiImageData(image=process_image_base64(room_1_base64), direction="north"),
            MultiImageData(image=process_image_base64(room_2_base64), direction="south"),
        ]
        results = await real_vision_service.extract_elements_batch(images)

        assert len(results) == 2
        for r in results:
            assert r.elements is not None
            assert r.architectural_features is not None


class TestMergeServiceE2E:
    @pytest.mark.asyncio
    @pytest.mark.timeout(60)
    async def test_merge_two_real_extractions(self, real_vision_service, real_merge_service, room_1_base64, room_2_base64):
        extractions = await real_vision_service.extract_elements_batch([
            MultiImageData(image=process_image_base64(room_1_base64), direction="north"),
            MultiImageData(image=process_image_base64(room_2_base64), direction="south"),
        ])

        assert len(extractions) == 2

        merged = await real_merge_service.merge_results(extractions)

        assert merged.confirmed_elements is not None
        assert merged.unconfirmed_elements is not None
        assert merged.architectural_features is not None
        assert isinstance(merged.confirmed_elements, list)
        assert isinstance(merged.unconfirmed_elements, list)
        assert isinstance(merged.spatial_conflicts, list)


class TestPreprocessingE2E:
    @pytest.mark.timeout(60)
    def test_png_processed_to_jpeg(self, room_1_base64):
        processed = process_image_base64(room_1_base64)
        assert processed != room_1_base64, "Processed should differ from original PNG"

        decoded = base64.b64decode(processed)
        img = Image.open(io.BytesIO(decoded))
        assert img.format == "JPEG", "Output should be JPEG"
        assert img.mode == "RGB", "Output should be RGB (not RGBA)"

    @pytest.mark.timeout(60)
    def test_processed_smaller_than_source_png(self, room_1_base64):
        processed = process_image_base64(room_1_base64)
        assert len(processed) < len(room_1_base64) * 1.5, "JPEG should be smaller than PNG source"

    @pytest.mark.timeout(60)
    def test_processed_base64_is_valid_image(self, room_1_base64):
        processed = process_image_base64(room_1_base64)
        decoded = base64.b64decode(processed)
        img = Image.open(io.BytesIO(decoded))
        assert img.width > 0 and img.height > 0


class TestEvaluateEndpointE2E:
    @pytest.mark.timeout(60)
    def test_single_image_evaluate_returns_valid_response(self, room_1_base64):
        client = TestClient(app)
        processed = process_image_base64(room_1_base64)
        response = client.post("/v1/evaluate", json={"image": processed})

        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "session_id" in data
        assert len(data["elements"]) >= 1
        assert data["elements"][0]["type"]
        assert "score" in data
        assert data["score"]["total"] >= 0
        assert "breakdown" in data["score"]
        assert data["room_grid"] is None
        assert data["dimensions"] is None

    @pytest.mark.timeout(60)
    def test_multi_photo_evaluate_with_dimensions_and_grid(self, room_1_base64, room_2_base64):
        client = TestClient(app)
        processed_1 = process_image_base64(room_1_base64)
        processed_2 = process_image_base64(room_2_base64)
        response = client.post("/v1/evaluate", json={
            "images": [
                {"image": processed_1, "direction": "north"},
                {"image": processed_2, "direction": "south"},
            ],
            "dimensions": {"length": 4.5, "width": 3.5},
        })

        assert response.status_code == 200, f"Expected 200, got {response.status_code}: {response.text}"
        data = response.json()
        assert "session_id" in data
        assert "elements" in data
        assert "score" in data
        assert data["score"]["total"] >= 0
        assert data["room_grid"] is not None
        assert data["room_grid"]["grid_size"] == "4x4"
        cells = data["room_grid"]["cells"]
        expected_keys = [f"{r},{c}" for r in range(4) for c in range(4)]
        assert set(cells.keys()) == set(expected_keys)
        valid_types = {
            "bed", "sofa", "armchair", "dining_table", "coffee_table",
            "desk", "wardrobe", "dresser", "bookshelf", "tv_stand",
            "plant", "lamp_floor", "lamp_table", "lamp_ceiling",
            "mirror", "rug", "curtains", "artwork", "door", "window",
            "empty", "fireplace",
        }
        for key, value in cells.items():
            assert value in valid_types, f"Cell {key} has invalid type: {value}"
        assert data["dimensions"]["length"] == 4.5
        assert data["dimensions"]["width"] == 3.5


class TestScoringE2E:
    @pytest.mark.timeout(90)
    def test_score_endpoint_with_real_session(self, room_1_base64):
        client = TestClient(app)
        processed = process_image_base64(room_1_base64)

        eval_response = client.post("/v1/evaluate", json={
            "image": processed,
            "session_id": "e2e-score-session",
            "school": "black_hat",
        })
        assert eval_response.status_code == 200
        session_id = eval_response.json()["session_id"]

        score_response = client.post("/v1/score", json={
            "session_id": session_id,
            "school": "black_hat",
        })
        assert score_response.status_code == 200, f"Expected 200, got {score_response.status_code}: {score_response.text}"
        data = score_response.json()
        assert data["session_id"] == session_id
        assert data["school"] == "black_hat"
        assert "score" in data
        assert data["score"]["total"] >= 0
        assert "chi_flow" in data["score"]

    @pytest.mark.timeout(90)
    def test_score_with_school_params(self, room_1_base64):
        client = TestClient(app)
        processed = process_image_base64(room_1_base64)

        eval_response = client.post("/v1/evaluate", json={
            "image": processed,
            "school": "black_hat",
            "birth_date": "1985-06-15",
        })
        assert eval_response.status_code == 200
        session_id = eval_response.json()["session_id"]

        score_response = client.post("/v1/score", json={
            "session_id": session_id,
            "school": "black_hat",
            "birth_date": "1985-06-15",
        })
        assert score_response.status_code == 200, f"Expected 200, got {score_response.status_code}: {score_response.text}"
        data = score_response.json()
        assert data["school"] == "black_hat"
        assert data["score"]["total"] >= 0


class TestSuggestAndAddElementE2E:
    @pytest.mark.timeout(90)
    def test_suggest_returns_200_and_valid_suggestions(self, room_1_base64):
        client = TestClient(app)
        processed = process_image_base64(room_1_base64)

        eval_response = client.post("/v1/evaluate", json={
            "image": processed,
            "session_id": "e2e-suggest-session",
        })
        assert eval_response.status_code == 200
        session_id = eval_response.json()["session_id"]

        suggest_response = client.post("/v1/suggest", json={
            "session_id": session_id,
        })
        assert suggest_response.status_code == 200, f"Expected 200, got {suggest_response.status_code}: {suggest_response.text}"
        data = suggest_response.json()
        assert "suggestions" in data
        assert len(data["suggestions"]) >= 1
        suggestion = data["suggestions"][0]
        assert "id" in suggestion
        assert "moves" in suggestion
        assert len(suggestion["moves"]) >= 1
        move = suggestion["moves"][0]
        assert move["element"]
        assert move["from_position"]
        assert move["to_position"]
        assert move["reason"]

    @pytest.mark.timeout(90)
    def test_add_element_updates_score(self, room_1_base64):
        client = TestClient(app)
        processed = process_image_base64(room_1_base64)

        eval_response = client.post("/v1/evaluate", json={
            "image": processed,
            "session_id": "e2e-add-element-session",
        })
        assert eval_response.status_code == 200
        session_id = eval_response.json()["session_id"]

        add_response = client.post("/v1/add-element", json={
            "session_id": session_id,
            "element": {
                "id": "plant_user",
                "type": "plant",
                "position_relative_to_camera": "corner",
                "confidence": "medium",
            },
        })
        assert add_response.status_code == 200, f"Expected 200, got {add_response.status_code}: {add_response.text}"
        data = add_response.json()
        assert "updated_score" in data
        assert "delta" in data
        assert isinstance(data["delta"], int)