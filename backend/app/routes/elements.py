from fastapi import APIRouter

from app.core.logger import get_logger, redact_session_id
from app.models.schemas import AddElementRequest, AddElementResponse, Score, Issue
from app.services.session import append_elements

logger = get_logger("elements")

router = APIRouter(tags=["elements"])

MOCK_UPDATED_SCORE = Score(
    total=79,
    chi_flow="flowing",
    breakdown={
        "commanding_position": {"score": 20, "max": 25, "status": "good"},
        "bagua_alignment": {"score": 15, "max": 20, "status": "good"},
        "chi_flow": {"score": 16, "max": 20, "status": "good"},
        "five_elements_balance": {"score": 12, "max": 15, "status": "needs_improvement"},
        "light_and_air": {"score": 8, "max": 10, "status": "good"},
        "mirror_placement": {"score": 8, "max": 10, "status": "good"},
    },
    issues=[
        Issue(
            issue="Sofa faces window instead of door",
            zone="Career",
            score_impact=-5,
            explanation="The sofa's commanding position is slightly improved with the added plant.",
        ),
    ],
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