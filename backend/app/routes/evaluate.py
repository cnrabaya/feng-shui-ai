import uuid
from fastapi import APIRouter

from app.models.schemas import (
    EvaluateRequest,
    EvaluateResponse,
    Score,
    ScoreBreakdown,
    Issue,
)

router = APIRouter(tags=["evaluate"])

MOCK_ELEMENTS = [
    {"id": "sofa_1", "type": "sofa", "position": "center", "orientation": "facing east"},
    {"id": "coffee_table_1", "type": "coffee_table", "position": "center-south", "orientation": "horizontal"},
    {"id": "tv_1", "type": "tv_stand", "position": "west wall", "orientation": "facing east"},
    {"id": "plant_1", "type": "plant", "position": "southeast corner", "orientation": "upright"},
    {"id": "lamp_1", "type": "floor_lamp", "position": "near sofa", "orientation": "vertical"},
]

MOCK_SCORE = Score(
    total=72,
    breakdown=ScoreBreakdown(
        commanding_position=18,
        bagua_alignment=14,
        chi_flow=15,
        five_elements_balance=10,
        light_and_air=8,
        mirror_placement=7,
    ),
    issues=[
        Issue(
            issue="Sofa faces window instead of door",
            zone="Career",
            score_impact=-7,
            explanation="The sofa's commanding position is disrupted as it faces a window rather than the entrance door.",
        ),
        Issue(
            issue="Cluttered walkway blocking chi flow",
            zone="Health",
            score_impact=-5,
            explanation="Items near the entrance block the natural flow of chi into the room.",
        ),
    ],
    chi_flow="restricted",
)


@router.post("/evaluate", response_model=EvaluateResponse)
async def evaluate_room(request: EvaluateRequest) -> EvaluateResponse:
    session_id = request.session_id or str(uuid.uuid4())
    return EvaluateResponse(
        session_id=session_id,
        elements=MOCK_ELEMENTS,
        score=MOCK_SCORE,
    )