import pytest
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
from app.main import app
from app.models.schemas import (
    ExtractionResult,
    DetectedElement,
    ArchitecturalFeatures,
    MergedRoom,
    RoomGrid,
    Score,
    Issue,
)


def make_mock_extraction(type_: str = "sofa") -> ExtractionResult:
    return ExtractionResult(
        elements=[DetectedElement(id=f"{type_}_1", type=type_, position_relative_to_camera="center", confidence="high")],
        architectural_features=ArchitecturalFeatures(doors=["north"], windows=["east"], visible_walls=["north", "east"]),
    )


def make_mock_merged_with_elements(elements: list[DetectedElement], room_grid: RoomGrid | None = None) -> MergedRoom:
    return MergedRoom(
        confirmed_elements=elements,
        unconfirmed_elements=[],
        architectural_features=ArchitecturalFeatures(doors=["north"], windows=["east"], visible_walls=["north", "east"]),
        spatial_conflicts=[],
        room_grid=room_grid,
    )


def make_mock_room_grid() -> RoomGrid:
    cells = {f"{r},{c}": "empty" for r in range(4) for c in range(4)}
    cells["0,0"] = "sofa"
    cells["0,1"] = "sofa"
    return RoomGrid(cells=cells)


def make_mock_score(
    total: int = 75,
    chi_flow: str = "good",
    breakdown: dict | None = None,
    issues: list | None = None,
) -> dict:
    return {
        "total_score": total,
        "chi_flow": chi_flow,
        "breakdown": breakdown or {
            "commanding_position": {"score": 20, "max": 25, "status": "good"},
            "bagua_alignment": {"score": 15, "max": 20, "status": "good"},
        },
        "issues": issues or [],
        "overall_assessment": "Room is reasonably balanced.",
        "school_specific": {},
    }


@pytest.fixture
def client():
    return TestClient(app)


class TestHealthEndpoint:
    def test_health_returns_ok(self, client: TestClient):
        response = client.get("/v1/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestEvaluateEndpoint:
    def test_evaluate_single_image_returns_elements(self, client: TestClient):
        mock_result = make_mock_extraction()
        with patch("app.routes.evaluate.process_image_base64", return_value="processed_fake_base64"), \
             patch("app.routes.evaluate.vision_service.extract_elements", new_callable=AsyncMock, return_value=mock_result), \
             patch("app.routes.evaluate.scoring_service.score", new_callable=AsyncMock, return_value=make_mock_score()):
            response = client.post("/v1/evaluate", json={"image": "fake_base64_data"})

        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "elements" in data
        assert len(data["elements"]) == 1
        assert data["elements"][0]["type"] == "sofa"
        assert "score" in data
        assert data["room_grid"] is None
        assert data["dimensions"] is None

    def test_evaluate_single_image_stores_session(self, client: TestClient):
        mock_result = make_mock_extraction()
        with patch("app.routes.evaluate.process_image_base64", return_value="processed_fake_base64"), \
             patch("app.routes.evaluate.vision_service.extract_elements", new_callable=AsyncMock, return_value=mock_result), \
             patch("app.routes.evaluate.scoring_service.score", new_callable=AsyncMock, return_value=make_mock_score()):
            response = client.post("/v1/evaluate", json={"image": "fake_base64_data"})

        assert response.status_code == 200
        data = response.json()
        assert len(data["session_id"]) > 0

    def test_evaluate_multi_photo_calls_batch_and_merge(self, client: TestClient):
        extraction1 = make_mock_extraction("sofa")
        extraction2 = make_mock_extraction("sofa")
        mock_grid = make_mock_room_grid()
        mock_merged = make_mock_merged_with_elements([extraction1.elements[0], extraction2.elements[0]], room_grid=mock_grid)
        with patch("app.routes.evaluate.process_image_base64", return_value="processed_fake_base64"), \
             patch("app.routes.evaluate.vision_service.extract_elements_batch", new_callable=AsyncMock, return_value=[extraction1, extraction2]), \
             patch("app.routes.evaluate.merge_service.merge_results", new_callable=AsyncMock, return_value=mock_merged), \
             patch("app.routes.evaluate.layout_service.generate_grid", new_callable=AsyncMock, return_value=mock_grid), \
             patch("app.routes.evaluate.scoring_service.score", new_callable=AsyncMock, return_value=make_mock_score()):
            response = client.post("/v1/evaluate", json={
                "images": [
                    {"image": "fake_base64_1", "direction": "north"},
                    {"image": "fake_base64_2", "direction": "south"},
                ],
                "dimensions": {"length": 4.5, "width": 3.5},
            })

        assert response.status_code == 200
        data = response.json()
        assert len(data["elements"]) == 2
        assert data["room_grid"] is not None
        assert data["dimensions"] is not None
        assert data["dimensions"]["length"] == 4.5
        assert data["dimensions"]["width"] == 3.5
        assert "grid_size" in data["room_grid"]
        assert "cells" in data["room_grid"]

    def test_evaluate_validation_error_no_image_no_images(self, client: TestClient):
        response = client.post("/v1/evaluate", json={})
        assert response.status_code == 422

    def test_evaluate_with_session_id_preserved(self, client: TestClient):
        mock_result = make_mock_extraction()
        session = "my-test-session-id"
        with patch("app.routes.evaluate.process_image_base64", return_value="processed_fake_base64"), \
             patch("app.routes.evaluate.vision_service.extract_elements", new_callable=AsyncMock, return_value=mock_result), \
             patch("app.routes.evaluate.scoring_service.score", new_callable=AsyncMock, return_value=make_mock_score()):
            response = client.post("/v1/evaluate", json={"image": "fake_base64", "session_id": session})

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session
        assert data["room_grid"] is None
        assert data["dimensions"] is None

    def test_evaluate_empty_images_list_rejected(self, client: TestClient):
        response = client.post("/v1/evaluate", json={"images": []})
        assert response.status_code == 422

    def test_evaluate_images_without_dimensions_returns_422(self, client: TestClient):
        with patch("app.routes.evaluate.process_image_base64", return_value="processed_fake_base64"), \
             patch("app.routes.evaluate.vision_service.extract_elements_batch", new_callable=AsyncMock), \
             patch("app.routes.evaluate.merge_service.merge_results", new_callable=AsyncMock), \
             patch("app.routes.evaluate.scoring_service.score", new_callable=AsyncMock, return_value=make_mock_score()):
            response = client.post("/v1/evaluate", json={
                "images": [
                    {"image": "fake_base64_1", "direction": "north"},
                    {"image": "fake_base64_2", "direction": "south"},
                ],
            })
        assert response.status_code == 422

    def test_evaluate_with_school_and_birth_date(self, client: TestClient):
        mock_result = make_mock_extraction()
        with patch("app.routes.evaluate.process_image_base64", return_value="processed_fake_base64"), \
             patch("app.routes.evaluate.vision_service.extract_elements", new_callable=AsyncMock, return_value=mock_result), \
             patch("app.routes.evaluate.scoring_service.score", new_callable=AsyncMock, return_value=make_mock_score()):
            response = client.post("/v1/evaluate", json={
                "image": "fake_base64",
                "school": "black_hat",
                "birth_date": "1990-01-01",
            })

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"]

    def test_evaluate_multi_photo_with_dimensions_generates_grid(self, client: TestClient):
        extraction1 = make_mock_extraction("sofa")
        extraction2 = make_mock_extraction("chair")
        mock_grid = make_mock_room_grid()
        mock_merged = make_mock_merged_with_elements(
            [extraction1.elements[0], extraction2.elements[0]], room_grid=mock_grid
        )
        with patch("app.routes.evaluate.process_image_base64", return_value="processed_fake_base64"), \
             patch("app.routes.evaluate.vision_service.extract_elements_batch", new_callable=AsyncMock, return_value=[extraction1, extraction2]), \
             patch("app.routes.evaluate.merge_service.merge_results", new_callable=AsyncMock, return_value=mock_merged), \
             patch("app.routes.evaluate.layout_service.generate_grid", new_callable=AsyncMock, return_value=mock_grid), \
             patch("app.routes.evaluate.scoring_service.score", new_callable=AsyncMock, return_value=make_mock_score()):
            response = client.post("/v1/evaluate", json={
                "images": [
                    {"image": "fake_base64_1", "direction": "north"},
                    {"image": "fake_base64_2", "direction": "south"},
                ],
                "dimensions": {"length": 5.0, "width": 4.0},
            })

        assert response.status_code == 200
        data = response.json()
        assert data["room_grid"] is not None
        assert data["room_grid"]["grid_size"] == "4x4"
        cells = data["room_grid"]["cells"]
        expected_keys = [f"{r},{c}" for r in range(4) for c in range(4)]
        assert set(cells.keys()) == set(expected_keys)
        assert data["dimensions"]["length"] == 5.0
        assert data["dimensions"]["width"] == 4.0

    def test_evaluate_single_image_without_dimensions_no_grid(self, client: TestClient):
        mock_result = make_mock_extraction()
        with patch("app.routes.evaluate.process_image_base64", return_value="processed_fake_base64"), \
             patch("app.routes.evaluate.vision_service.extract_elements", new_callable=AsyncMock, return_value=mock_result), \
             patch("app.routes.evaluate.scoring_service.score", new_callable=AsyncMock, return_value=make_mock_score()):
            response = client.post("/v1/evaluate", json={"image": "fake_base64"})

        assert response.status_code == 200
        data = response.json()
        assert data["room_grid"] is None

    def test_evaluate_stores_school_and_birth_date_in_session(self, client: TestClient):
        from app.services.session import get_stored_session_data

        mock_result = make_mock_extraction()
        with patch("app.routes.evaluate.process_image_base64", return_value="processed_fake_base64"), \
             patch("app.routes.evaluate.vision_service.extract_elements", new_callable=AsyncMock, return_value=mock_result), \
             patch("app.routes.evaluate.scoring_service.score", new_callable=AsyncMock, return_value=make_mock_score()):
            response = client.post("/v1/evaluate", json={
                "image": "fake_base64",
                "school": "form",
                "birth_date": "1985-06-15",
                "session_id": "session-with-school",
            })

        assert response.status_code == 200
        session_data = get_stored_session_data("session-with-school")
        assert session_data is not None
        assert session_data["school"] == "form"

    def test_evaluate_returns_score_with_breakdown(self, client: TestClient):
        mock_result = make_mock_extraction()
        mock_score = make_mock_score(
            total=82,
            chi_flow="flowing",
            breakdown={"commanding_position": {"score": 20, "max": 25, "status": "good"}},
        )
        with patch("app.routes.evaluate.process_image_base64", return_value="processed_fake_base64"), \
             patch("app.routes.evaluate.vision_service.extract_elements", new_callable=AsyncMock, return_value=mock_result), \
             patch("app.routes.evaluate.scoring_service.score", new_callable=AsyncMock, return_value=mock_score):
            response = client.post("/v1/evaluate", json={"image": "fake_base64"})

        assert response.status_code == 200
        data = response.json()
        assert "score" in data
        assert data["score"]["total"] == 82
        assert data["score"]["chi_flow"] == "flowing"
        assert "breakdown" in data["score"]

    def test_evaluate_calls_scoring_service_with_correct_elements(self, client: TestClient):
        mock_result = make_mock_extraction("plant")
        mock_score = make_mock_score()
        scoring_call_args = {}

        async def mock_score_fn(**kwargs):
            scoring_call_args["elements"] = kwargs.get("elements")
            scoring_call_args["school"] = kwargs.get("school")
            return mock_score

        with patch("app.routes.evaluate.process_image_base64", return_value="processed_fake_base64"), \
             patch("app.routes.evaluate.vision_service.extract_elements", new_callable=AsyncMock, return_value=mock_result), \
             patch("app.routes.evaluate.scoring_service.score", new_callable=AsyncMock, side_effect=mock_score_fn):
            response = client.post("/v1/evaluate", json={"image": "fake_base64", "school": "black_hat"})

        assert response.status_code == 200
        assert "elements" in scoring_call_args
        assert len(scoring_call_args["elements"]) == 1
        assert scoring_call_args["elements"][0]["type"] == "plant"
        assert scoring_call_args["school"] == "black_hat"