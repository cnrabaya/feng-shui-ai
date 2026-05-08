import pytest
from unittest.mock import AsyncMock, patch

from app.services.scoring import ScoringService


MINIMAL_MOCK_RESPONSE = '{"total_score": 75, "chi_flow": "good", "breakdown": {}, "issues": []}'


def make_mock_response(content: str):
    mock_choice = type("MockChoice", (), {
        "message": type("MockMessage", (), {"content": content})()
    })()
    return type("MockResponse", (), {"choices": [mock_choice]})()


@pytest.fixture
def scoring_service():
    return ScoringService()


class TestScoringServiceInstantiation:
    def test_scoring_service_instantiation(self, scoring_service: ScoringService):
        assert scoring_service is not None
        assert scoring_service.model is not None
        assert scoring_service.client is not None


class TestScoringServiceFormatPrompt:
    def test_format_prompt_contains_elements(self, scoring_service: ScoringService):
        elements = [{"id": "sofa_1", "type": "sofa", "position": "center"}]
        prompt = scoring_service._format_prompt(school="black_hat", elements=elements)

        assert "sofa" in prompt
        assert "Black Hat" in prompt
        assert '"id": "sofa_1"' in prompt

    def test_format_prompt_default_school(self, scoring_service: ScoringService):
        prompt = scoring_service._format_prompt(school="black_hat", elements=[])
        assert "Black Hat" in prompt

    def test_format_prompt_with_dimensions(self, scoring_service: ScoringService):
        from app.models.schemas import Dimensions
        dims = Dimensions(length=5.0, width=4.0, unit="meters")
        prompt = scoring_service._format_prompt(school="black_hat", elements=[], dimensions=dims)

        assert "5.0" in prompt
        assert "4.0" in prompt
        assert "meters" in prompt

    def test_format_prompt_without_dimensions(self, scoring_service: ScoringService):
        prompt = scoring_service._format_prompt(school="black_hat", elements=[], dimensions=None)
        assert "not provided" in prompt


class TestScoringServiceParseResponse:
    def test_parse_score_response_valid_json(self, scoring_service: ScoringService):
        raw = '{"total_score": 75, "chi_flow": "good", "breakdown": {}, "issues": []}'
        result = scoring_service._parse_score_response(raw)

        assert isinstance(result, dict)
        assert result["total_score"] == 75
        assert result["chi_flow"] == "good"

    def test_parse_score_response_with_surrounding_text(self, scoring_service: ScoringService):
        raw = 'NOT JSON\n{"total_score": 82, "chi_flow": "moderate", "breakdown": {}, "issues": []}\nMORE TEXT'
        result = scoring_service._parse_score_response(raw)

        assert result["total_score"] == 82
        assert result["chi_flow"] == "moderate"

    def test_parse_score_response_invalid_raises_error(self, scoring_service: ScoringService):
        raw = "this is not json at all {{{{"
        with pytest.raises(ValueError):
            scoring_service._parse_score_response(raw)


class TestScoringServiceScore:
    @pytest.mark.anyio(backend="asyncio")
    async def test_score_method_with_mocked_llm(self, scoring_service: ScoringService):
        mock_response = make_mock_response(MINIMAL_MOCK_RESPONSE)

        with patch.object(scoring_service.client, "chat",
            type("MockChat", (), {"completions": type("MockCompletions", (),
                {"create": AsyncMock(return_value=mock_response)})()})()):

            elements = [{"id": "chair_1", "type": "chair", "position": "corner"}]
            result = await scoring_service.score(elements=elements, school="black_hat")

        assert isinstance(result, dict)
        assert result["total_score"] == 75
        assert result["chi_flow"] == "good"
        assert result["breakdown"] == {}
        assert result["issues"] == []

    @pytest.mark.anyio(backend="asyncio")
    async def test_score_method_with_all_params(self, scoring_service: ScoringService):
        mock_response = make_mock_response(MINIMAL_MOCK_RESPONSE)

        with patch.object(scoring_service.client, "chat",
            type("MockChat", (), {"completions": type("MockCompletions", (),
                {"create": AsyncMock(return_value=mock_response)})()})()):

            from app.models.schemas import Dimensions
            dims = Dimensions(length=6.0, width=5.0, unit="meters")
            elements = [{"id": "bed_1", "type": "bed", "position": "center"}]

            result = await scoring_service.score(
                elements=elements,
                school="form",
                dimensions=dims,
                birth_date="1990-01-15",
                kua_number=5,
                building_date="2020-06-01",
            )

        assert result["total_score"] == 75

    @pytest.mark.anyio(backend="asyncio")
    async def test_score_multiple_schools(self, scoring_service: ScoringService):
        mock_response = make_mock_response(MINIMAL_MOCK_RESPONSE)

        with patch.object(scoring_service.client, "chat",
            type("MockChat", (), {"completions": type("MockCompletions", (),
                {"create": AsyncMock(return_value=mock_response)})()})()):

            elements = [{"id": "table_1", "type": "table", "position": "center"}]

            for school in ["black_hat", "form", "compass"]:
                result = await scoring_service.score(elements=elements, school=school)
                assert result["total_score"] == 75

    @pytest.mark.anyio(backend="asyncio")
    async def test_score_retries_on_failure_and_succeeds(self, scoring_service: ScoringService):
        mock_fail = make_mock_response("server error")
        mock_success = make_mock_response(MINIMAL_MOCK_RESPONSE)

        call_count = 0

        async def mock_create(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Connection error")
            return mock_success

        with patch.object(scoring_service.client, "chat",
            type("MockChat", (), {"completions": type("MockCompletions", (),
                {"create": mock_create})()})()):

            result = await scoring_service.score(elements=[{"id": "c", "type": "chair"}], school="black_hat")

        assert call_count == 3
        assert result["total_score"] == 75

    @pytest.mark.anyio(backend="asyncio")
    async def test_score_retries_on_parse_error_and_succeeds(self, scoring_service: ScoringService):
        mock_fail = make_mock_response("not valid json {{{")
        mock_success = make_mock_response(MINIMAL_MOCK_RESPONSE)

        call_count = 0

        async def mock_create(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                return mock_fail
            return mock_success

        with patch.object(scoring_service.client, "chat",
            type("MockChat", (), {"completions": type("MockCompletions", (),
                {"create": mock_create})()})()):

            result = await scoring_service.score(elements=[{"id": "c", "type": "chair"}], school="black_hat")

        assert call_count == 3
        assert result["total_score"] == 75

    @pytest.mark.parametrize("school", ["black_hat", "form", "three_door", "five_elements", "compass"])
    @pytest.mark.anyio(backend="asyncio")
    async def test_score_all_five_schools(self, scoring_service: ScoringService, school: str):
        mock_response = make_mock_response(MINIMAL_MOCK_RESPONSE)

        with patch.object(scoring_service.client, "chat",
            type("MockChat", (), {"completions": type("MockCompletions", (),
                {"create": AsyncMock(return_value=mock_response)})()})()):

            result = await scoring_service.score(elements=[], school=school)

        assert result["total_score"] == 75