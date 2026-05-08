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


class TestScoreEndpoint:
    def test_score_returns_valid_schema(self, client: TestClient):
        extraction = ExtractionResult(
            elements=[DetectedElement(id="sofa_1", type="sofa", position_relative_to_camera="center", confidence="high")],
            architectural_features=ArchitecturalFeatures(),
        )
        session_module.store_extraction_result("score-test-session", extraction, school="black_hat")

        response = client.post("/v1/score", json={
            "session_id": "score-test-session",
            "school": "black_hat",
        })

        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert data["session_id"] == "score-test-session"
        assert "school" in data
        assert data["school"] == "black_hat"
        assert "score" in data
        assert "total" in data["score"]
        assert isinstance(data["score"]["total"], int)

    def test_score_session_not_found_returns_404(self, client: TestClient):
        response = client.post("/v1/score", json={
            "session_id": "nonexistent-session",
            "school": "black_hat",
        })
        assert response.status_code == 404

    def test_score_missing_session_id_returns_422(self, client: TestClient):
        response = client.post("/v1/score", json={})
        assert response.status_code == 422