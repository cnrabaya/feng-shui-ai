import pytest
from app.services import session as session_module
from app.models.schemas import ExtractionResult, DetectedElement, ArchitecturalFeatures, MergedRoom, RoomGrid, Dimensions


def make_extraction(type_: str = "sofa") -> ExtractionResult:
    return ExtractionResult(
        elements=[DetectedElement(id=f"{type_}_1", type=type_, position_relative_to_camera="center", confidence="high")],
        architectural_features=ArchitecturalFeatures(doors=["north"], windows=["east"], visible_walls=["north", "east"]),
    )


def make_merged(elements: list[DetectedElement], room_grid: RoomGrid | None = None) -> MergedRoom:
    return MergedRoom(
        confirmed_elements=elements,
        unconfirmed_elements=[],
        architectural_features=ArchitecturalFeatures(doors=["north"], windows=["east"], visible_walls=["north", "east"]),
        spatial_conflicts=[],
        room_grid=room_grid,
    )


def make_room_grid() -> RoomGrid:
    cells = {f"{r},{c}": "empty" for r in range(4) for c in range(4)}
    cells["0,0"] = "sofa"
    return RoomGrid(cells=cells)


@pytest.fixture(autouse=True)
def clean_session_store():
    session_module._session_store.clear()
    yield
    session_module._session_store.clear()


class TestSessionStoreAndRetrieve:
    def test_store_and_get_extraction_result(self):
        extraction = make_extraction("plant")
        session_module.store_extraction_result("session-1", extraction, school="black_hat")

        result = session_module.get_extraction_result("session-1")
        assert result is not None
        assert isinstance(result, ExtractionResult)
        assert len(result.elements) == 1
        assert result.elements[0].type == "plant"

    def test_store_and_get_merged_result(self):
        merged = make_merged([DetectedElement(id="desk_1", type="desk", position_relative_to_camera="center", confidence="high")])
        session_module.store_merged_result("session-2", merged, school="form")

        result = session_module.get_merged_result("session-2")
        assert result is not None
        assert isinstance(result, MergedRoom)
        assert len(result.confirmed_elements) == 1
        assert result.confirmed_elements[0].type == "desk"

    def test_get_stored_elements_and_school(self):
        extraction = make_extraction("chair")
        session_module.store_extraction_result("session-3", extraction, school="compass")

        stored = session_module.get_stored_elements_and_school("session-3")
        assert stored is not None
        elements, school = stored
        assert school == "compass"
        assert len(elements) == 1
        assert elements[0]["type"] == "chair"

    def test_append_elements_marks_user_added(self):
        extraction = make_extraction("bed")
        session_module.store_extraction_result("session-4", extraction, school="black_hat")

        session_module.append_elements("session-4", [{"id": "plant_user", "type": "plant", "position_relative_to_camera": "corner", "confidence": "medium"}])

        stored = session_module.get_stored_elements_and_school("session-4")
        assert stored is not None
        elements, _ = stored
        assert len(elements) == 2
        user_added = next(e for e in elements if e["id"] == "plant_user")
        assert user_added["confidence"] == "user_added"

    def test_get_stored_session_data_full(self):
        merged = make_merged(
            [DetectedElement(id="sofa_1", type="sofa", position_relative_to_camera="center", confidence="high")],
            room_grid=make_room_grid(),
        )
        dims = Dimensions(length=5.0, width=4.0)
        session_module.store_merged_result("session-5", merged, school="form", dimensions=dims)

        data = session_module.get_stored_session_data("session-5")
        assert data is not None
        assert data["school"] == "form"
        assert data["dimensions"] == dims
        assert len(data["elements"]) == 1
        assert data["result"].room_grid is not None
        assert data["result"].room_grid.cells["0,0"] == "sofa"

    def test_session_not_found_returns_none(self):
        assert session_module.get_extraction_result("unknown-id") is None
        assert session_module.get_merged_result("unknown-id") is None
        assert session_module.get_stored_elements_and_school("unknown-id") is None
        assert session_module.get_stored_session_data("unknown-id") is None

    def test_append_elements_unknown_session_raises(self):
        with pytest.raises(ValueError, match="Session .* not found"):
            session_module.append_elements("nonexistent-session", [{"id": "x", "type": "x"}])