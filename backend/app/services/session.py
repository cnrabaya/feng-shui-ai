from app.models.schemas import ExtractionResult, DetectedElement, MergedRoom

_session_store: dict[str, ExtractionResult | MergedRoom] = {}


def store_extraction_result(session_id: str, result: ExtractionResult) -> None:
    _session_store[session_id] = result


def get_extraction_result(session_id: str) -> ExtractionResult | None:
    stored = _session_store.get(session_id)
    if stored is None:
        return None
    if isinstance(stored, MergedRoom):
        return None
    return stored


def store_merged_result(session_id: str, result: MergedRoom) -> None:
    _session_store[session_id] = result


def get_merged_result(session_id: str) -> MergedRoom | None:
    stored = _session_store.get(session_id)
    if stored is None:
        return None
    if isinstance(stored, ExtractionResult):
        return None
    return stored


def append_elements(session_id: str, new_elements: list[dict]) -> MergedRoom:
    stored = _session_store.get(session_id)
    if stored is None:
        raise ValueError(f"Session {session_id} not found")

    if isinstance(stored, ExtractionResult):
        merged = MergedRoom(
            confirmed_elements=stored.elements,
            unconfirmed_elements=[],
            architectural_features=stored.architectural_features,
        )
        _session_store[session_id] = merged
        stored = merged

    for elem_data in new_elements:
        elem = DetectedElement(**elem_data)
        elem.confidence = "user_added"
        stored.confirmed_elements.append(elem)

    return stored