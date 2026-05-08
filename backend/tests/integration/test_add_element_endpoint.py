import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.services import session as session_module
from app.models.schemas import ExtractionResult, DetectedElement, ArchitecturalFeatures


@pytest.fixture(autouse=True)
def clean_session():
    session_module._session_store.clear()
    yield
    session_module._session_store.clear()


@pytest.fixture
def client():
    return TestClient(app)


class TestAddElementEndpoint:
    def test_add_element_returns_200_and_delta(self, client: TestClient):
        extraction = ExtractionResult(
            elements=[DetectedElement(id="sofa_1", type="sofa", position_relative_to_camera="center", confidence="high")],
            architectural_features=ArchitecturalFeatures(),
        )
        session_module.store_extraction_result("test-session-add", extraction, school="black_hat")

        response = client.post("/v1/add-element", json={
            "session_id": "test-session-add",
            "element": {"id": "plant_1", "type": "plant", "position_relative_to_camera": "corner", "confidence": "medium"},
        })
        assert response.status_code == 200
        data = response.json()
        assert "updated_score" in data
        assert "delta" in data
        assert isinstance(data["delta"], int)

    def test_add_element_requires_session_id(self, client: TestClient):
        response = client.post("/v1/add-element", json={
            "element": {"id": "plant_1", "type": "plant"},
        })
        assert response.status_code == 422

    def test_add_element_requires_element(self, client: TestClient):
        response = client.post("/v1/add-element", json={
            "session_id": "any-session",
        })
        assert response.status_code == 422