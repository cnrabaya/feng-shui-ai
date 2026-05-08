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


class TestSuggestEndpoint:
    def test_suggest_returns_200_and_valid_suggestions(self, client: TestClient):
        response = client.post("/v1/suggest", json={"session_id": "any-session-id"})
        assert response.status_code == 200
        data = response.json()
        assert "suggestions" in data
        assert isinstance(data["suggestions"], list)
        assert len(data["suggestions"]) > 0
        suggestion = data["suggestions"][0]
        assert "id" in suggestion
        assert "moves" in suggestion
        assert isinstance(suggestion["moves"], list)
        assert len(suggestion["moves"]) > 0
        move = suggestion["moves"][0]
        assert "element" in move
        assert "from_position" in move
        assert "to_position" in move
        assert "reason" in move

    def test_suggest_requires_session_id(self, client: TestClient):
        response = client.post("/v1/suggest", json={})
        assert response.status_code == 422