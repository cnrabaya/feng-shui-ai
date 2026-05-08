from fastapi import APIRouter, HTTPException

from app.models.schemas import ScoreRequest, ScoreResponse, Score, Issue
from app.services.scoring import scoring_service
from app.services.session import get_stored_elements_and_school

router = APIRouter(tags=["score"])


@router.post("/score", response_model=ScoreResponse)
async def score_room(request: ScoreRequest) -> ScoreResponse:
    stored = get_stored_elements_and_school(request.session_id)
    if not stored:
        raise HTTPException(status_code=404, detail=f"Session {request.session_id} not found")

    elements, _ = stored

    result = await scoring_service.score(
        elements=elements,
        school=request.school,
        dimensions=None,
        birth_date=request.birth_date,
        kua_number=request.kua_number,
        building_date=request.building_date,
    )

    score_normalized = Score(
        total=result.get("total_score", result.get("total", 0)),
        chi_flow=str(result.get("chi_flow", "unknown")),
        breakdown=result.get("breakdown", {}),
        issues=[Issue(**issue) for issue in result.get("issues", [])],
        overall_assessment=result.get("overall_assessment"),
        school_specific=result.get("school_specific"),
    )

    missing_data = result.get("missing_data", None)

    return ScoreResponse(
        session_id=request.session_id,
        school=request.school,
        score=score_normalized,
        missing_data=missing_data,
    )