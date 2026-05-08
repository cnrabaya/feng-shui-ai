from typing import Optional
from app.models.schemas import ExtractionResult, DetectedElement, MergedRoom, Dimensions

_SessionData = dict  # alias for clarity


_session_store: dict[str, _SessionData] = {}


def store_extraction_result(
    session_id: str,
    result: ExtractionResult,
    school: str = "black_hat",
    dimensions: Optional[Dimensions] = None,
    grid_size: Optional[str] = None,
) -> None:
    _session_store[session_id] = {
        "result": result,
        "school": school,
        "dimensions": dimensions,
        "grid_size": grid_size,
        "elements": [
            {
                "id": e.id,
                "type": e.type,
                "position": e.position_relative_to_camera,
                "orientation": None,
                "confidence": e.confidence,
            }
            for e in result.elements
        ],
    }


def store_merged_result(
    session_id: str,
    result: MergedRoom,
    school: str = "black_hat",
    dimensions: Optional[Dimensions] = None,
    grid_size: Optional[str] = None,
) -> None:
    _session_store[session_id] = {
        "result": result,
        "school": school,
        "dimensions": dimensions,
        "grid_size": grid_size,
        "elements": [
            {
                "id": e.id,
                "type": e.type,
                "position": e.position_relative_to_camera,
                "orientation": None,
                "confidence": e.confidence,
            }
            for e in result.confirmed_elements + result.unconfirmed_elements
        ],
    }


def get_extraction_result(session_id: str) -> Optional[ExtractionResult]:
    stored = _session_store.get(session_id)
    if stored is None:
        return None
    result = stored.get("result")
    if isinstance(result, MergedRoom):
        return None
    return result


def get_merged_result(session_id: str) -> Optional[MergedRoom]:
    stored = _session_store.get(session_id)
    if stored is None:
        return None
    result = stored.get("result")
    if isinstance(result, ExtractionResult):
        return None
    return result


def get_stored_elements_and_school(session_id: str) -> Optional[tuple[list[dict], str]]:
    """Returns (elements_list, school) or None if session not found."""
    stored = _session_store.get(session_id)
    if stored is None:
        return None
    return stored.get("elements", []), stored.get("school", "black_hat")


def get_stored_session_data(session_id: str) -> Optional[_SessionData]:
    """Returns full session data including elements, school, dimensions."""
    return _session_store.get(session_id)


def append_elements(session_id: str, new_elements: list[dict]) -> MergedRoom:
    stored = _session_store.get(session_id)
    if stored is None:
        raise ValueError(f"Session {session_id} not found")

    result = stored.get("result")
    if isinstance(result, ExtractionResult):
        merged = MergedRoom(
            confirmed_elements=result.elements,
            unconfirmed_elements=[],
            architectural_features=result.architectural_features,
        )
        stored["result"] = merged
        result = merged

    for elem_data in new_elements:
        elem = DetectedElement(**elem_data)
        elem.confidence = "user_added"
        result.confirmed_elements.append(elem)

    stored["elements"] = [
        {
            "id": e.id,
            "type": e.type,
            "position": e.position_relative_to_camera,
            "orientation": None,
            "confidence": e.confidence,
        }
        for e in result.confirmed_elements + result.unconfirmed_elements
    ]

    return result