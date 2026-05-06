from fastapi import APIRouter

from app.models.schemas import SuggestRequest, SuggestResponse, Suggestion, Move

router = APIRouter(tags=["suggest"])

MOCK_SUGGESTIONS = [
    Suggestion(
        id=1,
        projected_score=88,
        moves=[
            Move(
                element="sofa",
                from_position="center of room",
                to_position="west wall, facing east",
                reason="Achieve commanding position - face the door without direct alignment",
            ),
            Move(
                element="coffee_table",
                from_position="center-south",
                to_position="in front of sofa",
                reason="Create clear pathway and improve chi flow",
            ),
        ],
        annotated_image=None,
    ),
    Suggestion(
        id=2,
        projected_score=85,
        moves=[
            Move(
                element="tv_stand",
                from_position="west wall",
                to_position="north wall",
                reason="Avoid reflecting the door in the TV screen",
            ),
            Move(
                element="plant",
                from_position="southeast corner",
                to_position="near entrance",
                reason="Strengthen Wealth zone by placing live plant near door",
            ),
        ],
        annotated_image=None,
    ),
    Suggestion(
        id=3,
        projected_score=82,
        moves=[
            Move(
                element="floor_lamp",
                from_position="near sofa",
                to_position="dark corner near southeast",
                reason="Illuminate the Wealth zone and balance the five elements",
            ),
        ],
        annotated_image=None,
    ),
]


@router.post("/suggest", response_model=SuggestResponse)
async def get_suggestions(request: SuggestRequest) -> SuggestResponse:
    return SuggestResponse(suggestions=MOCK_SUGGESTIONS)