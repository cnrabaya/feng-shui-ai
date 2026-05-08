import pytest
from app.services import session as session_module
from app.models.schemas import ExtractionResult, DetectedElement, ArchitecturalFeatures, MergedRoom, RoomGrid, Dimensions

pytestmark = pytest.mark.e2e


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
    cells["1,1"] = "sofa"
    cells["1,2"] = "sofa"
    cells["2,3"] = "plant"
    return RoomGrid(cells=cells)


@pytest.fixture(autouse=True)
def clean_session():
    session_module._session_store.clear()
    yield
    session_module._session_store.clear()


class TestSessionCleanup:
    def test_session_store_accepts_many_sessions(self):
        for i in range(50):
            extraction = make_extraction(f"item_{i}")
            session_module.store_extraction_result(f"session-{i:03d}", extraction, school="black_hat")

        for i in range(50):
            result = session_module.get_extraction_result(f"session-{i:03d}")
            assert result is not None, f"Session {i:03d} not found"
            assert len(result.elements) == 1
            assert result.elements[0].type == f"item_{i}"

    def test_session_cleanup_after_100_sessions(self):
        for i in range(100):
            extraction = make_extraction(f"item_{i}")
            session_module.store_extraction_result(f"bulk-session-{i:03d}", extraction, school="form")

        old_session = session_module.get_extraction_result("bulk-session-000")
        assert old_session is not None
        assert old_session.elements[0].type == "item_0"

        new_session = session_module.get_extraction_result("bulk-session-099")
        assert new_session is not None
        assert new_session.elements[0].type == "item_99"

    def test_session_with_room_grid_persists_correctly(self):
        grid = make_room_grid()
        merged = make_merged(
            [DetectedElement(id="sofa_1", type="sofa", position_relative_to_camera="center", confidence="high")],
            room_grid=grid,
        )
        dims = Dimensions(length=6.0, width=5.0)
        session_module.store_merged_result("grid-session", merged, school="compass", dimensions=dims)

        stored = session_module.get_stored_session_data("grid-session")
        assert stored is not None
        assert stored["school"] == "compass"
        assert stored["dimensions"] == dims
        assert stored["result"].room_grid is not None
        assert stored["result"].room_grid.cells["1,1"] == "sofa"
        assert stored["result"].room_grid.cells["2,3"] == "plant"
        assert len(stored["result"].room_grid.cells) == 16