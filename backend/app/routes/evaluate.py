import uuid
from fastapi import APIRouter

from app.models.schemas import (
    EvaluateRequest,
    EvaluateResponse,
    Score,
    ScoreBreakdown,
    Issue,
)
from app.services.scoring import calculate_feng_shui_score

router = APIRouter(tags=["evaluate"])

MOCK_ELEMENTS = [
    {"id": "sofa_1", "type": "sofa", "position": "center-south", "orientation": "facing east"},
    {"id": "coffee_table_1", "type": "coffee_table", "position": "center-south", "orientation": "horizontal"},
    {"id": "tv_1", "type": "tv_stand", "position": "west wall", "orientation": "facing east"},
    {"id": "plant_1", "type": "plant", "position": "southeast corner", "orientation": "upright"},
    {"id": "lamp_1", "type": "floor_lamp", "position": "near sofa", "orientation": "vertical"},
    {"id": "bed_1", "type": "bed", "position": "north wall", "orientation": "facing south"},
    {"id": "door_1", "type": "door", "position": "south wall", "orientation": "facing north"},
    {"id": "window_1", "type": "window", "position": "east wall", "orientation": "facing west"},
    {"id": "mirror_1", "type": "mirror", "position": "north wall", "orientation": "facing south"},
]


@router.post("/evaluate", response_model=EvaluateResponse)
async def evaluate_room(request: EvaluateRequest) -> EvaluateResponse:
    session_id = request.session_id or str(uuid.uuid4())

    result = calculate_feng_shui_score(MOCK_ELEMENTS, request.dimensions)

    return EvaluateResponse(
        session_id=session_id,
        elements=MOCK_ELEMENTS,
        score=Score(
            total=result["total"],
            breakdown=result["breakdown"],
            issues=result["issues"],
            chi_flow=result["chi_flow"],
        ),
    )