from fastapi import APIRouter

from app.core.logger import get_logger, redact_session_id
from app.models.schemas import AddElementRequest, AddElementResponse, Score, ScoreBreakdown, Issue
from app.services.session import append_elements

logger = get_logger("elements")

router = APIRouter(tags=["elements"])

MOCK_UPDATED_SCORE = Score(
    total=79,
    breakdown=ScoreBreakdown(
        commanding_position=20,
        bagua_alignment=15,
        chi_flow=16,
        five_elements_balance=12,
        light_and_air=8,
        mirror_placement=8,
    ),
    issues=[
        Issue(
            issue="Sofa faces window instead of door",
            zone="Career",
            score_impact=-5,
            explanation="The sofa's commanding position is slightly improved with the added plant.",
        ),
    ],
    chi_flow="flowing",
)


@router.post("/add-element", response_model=AddElementResponse)
async def add_element(request: AddElementRequest) -> AddElementResponse:
    element_type = request.element.get("type", "unknown")
    logger.info(f"Add element: session={redact_session_id(request.session_id)}, element_type={element_type}")
    append_elements(request.session_id, [request.element])
    return AddElementResponse(
        updated_score=MOCK_UPDATED_SCORE,
        delta=7,
    )