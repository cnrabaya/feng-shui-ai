import pytest
from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient
from app.main import app
from app.models.schemas import ExtractionResult, DetectedElement, ArchitecturalFeatures, MergedRoom


def make_mock_extraction(type_: str = "sofa") -> ExtractionResult:
    return ExtractionResult(
        elements=[DetectedElement(id=f"{type_}_1", type=type_, position_relative_to_camera="center", confidence="high")],
        architectural_features=ArchitecturalFeatures(doors=[{"location": "north"}], windows=[{"location": "east", "count": 1}], visible_walls=["north", "east"]),
    )


def make_mock_merged_with_elements(elements: list[DetectedElement]) -> MergedRoom:
    return MergedRoom(
        confirmed_elements=elements,
        unconfirmed_elements=[],
        architectural_features=ArchitecturalFeatures(doors=[{"location": "north"}], windows=[{"location": "east", "count": 1}], visible_walls=["north", "east"]),
        spatial_conflicts=[],
    )


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
             patch("app.routes.evaluate.vision_service.extract_elements", new_callable=AsyncMock, return_value=mock_result):
            response = client.post("/v1/evaluate", json={"image": "fake_base64_data"})

        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "elements" in data
        assert len(data["elements"]) == 1
        assert data["elements"][0]["type"] == "sofa"
        assert "score" in data

    def test_evaluate_single_image_stores_session(self, client: TestClient):
        mock_result = make_mock_extraction()
        with patch("app.routes.evaluate.process_image_base64", return_value="processed_fake_base64"), \
             patch("app.routes.evaluate.vision_service.extract_elements", new_callable=AsyncMock, return_value=mock_result):
            response = client.post("/v1/evaluate", json={"image": "fake_base64_data"})

        assert response.status_code == 200
        data = response.json()
        assert len(data["session_id"]) > 0

    def test_evaluate_multi_photo_calls_batch_and_merge(self, client: TestClient):
        extraction1 = make_mock_extraction("sofa")
        extraction2 = make_mock_extraction("sofa")
        mock_merged = make_mock_merged_with_elements([extraction1.elements[0], extraction2.elements[0]])
        with patch("app.routes.evaluate.process_image_base64", return_value="processed_fake_base64"), \
             patch("app.routes.evaluate.vision_service.extract_elements_batch", new_callable=AsyncMock, return_value=[extraction1, extraction2]), \
             patch("app.routes.evaluate.merge_service.merge_results", new_callable=AsyncMock, return_value=mock_merged):
            response = client.post("/v1/evaluate", json={
                "images": [
                    {"image": "fake_base64_1", "direction": "north"},
                    {"image": "fake_base64_2", "direction": "south"},
                ]
            })

        assert response.status_code == 200
        data = response.json()
        assert len(data["elements"]) == 2

    def test_evaluate_validation_error_no_image_no_images(self, client: TestClient):
        response = client.post("/v1/evaluate", json={})
        assert response.status_code == 422

    def test_evaluate_with_session_id_preserved(self, client: TestClient):
        mock_result = make_mock_extraction()
        session = "my-test-session-id"
        with patch("app.routes.evaluate.process_image_base64", return_value="processed_fake_base64"), \
             patch("app.routes.evaluate.vision_service.extract_elements", new_callable=AsyncMock, return_value=mock_result):
            response = client.post("/v1/evaluate", json={"image": "fake_base64", "session_id": session})

        assert response.status_code == 200
        data = response.json()
        assert data["session_id"] == session

    def test_evaluate_empty_images_list_rejected(self, client: TestClient):
        response = client.post("/v1/evaluate", json={"images": []})
        assert response.status_code == 422