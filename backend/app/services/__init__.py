from app.services.vision import VisionService, get_vision_service
from app.services.merge import MergeService, get_merge_service
from app.services.layout import LayoutService, get_layout_service
from app.services.scoring import ScoringService, get_scoring_service


def __getattr__(name: str):
    if name == "vision_service":
        from app.services.vision import get_vision_service

        return get_vision_service()
    if name == "merge_service":
        from app.services.merge import get_merge_service

        return get_merge_service()
    if name == "layout_service":
        from app.services.layout import get_layout_service

        return get_layout_service()
    if name == "scoring_service":
        from app.services.scoring import get_scoring_service

        return get_scoring_service()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")