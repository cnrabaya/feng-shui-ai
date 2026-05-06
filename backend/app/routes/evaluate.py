import uuid
from fastapi import APIRouter, Request, HTTPException

from app.core.logger import get_logger, redact_session_id
from app.models.schemas import (
    EvaluateRequest,
    EvaluateResponse,
    Score,
    ScoreBreakdown,
    Issue,
    MultiImageData,
)
from app.services.vision import vision_service
from app.services.merge import merge_service
from app.services.session import store_extraction_result, store_merged_result
from app.services.image_processor import process_image_base64

logger = get_logger("evaluate")

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
async def evaluate_room(request: EvaluateRequest, http_request: Request) -> EvaluateResponse:
    session_id = request.session_id or str(uuid.uuid4())

    if request.images:
        image_count = len(request.images)
        logger.info(f"Multi-photo evaluate: session={redact_session_id(session_id)}, images={image_count}")
        processed_images = [
            MultiImageData(image=process_image_base64(img.image), direction=img.direction)
            for img in request.images
        ]
        extractions = await vision_service.extract_elements_batch(processed_images)
        merged = await merge_service.merge_results(extractions)
        store_merged_result(session_id, merged)
        elements = [
            {
                "id": e.id,
                "type": e.type,
                "position": e.position_relative_to_camera,
                "orientation": None,
                "confidence": e.confidence,
            }
            for e in merged.confirmed_elements + merged.unconfirmed_elements
        ]
        logger.info(f"Multi-photo complete: session={redact_session_id(session_id)}, confirmed={len(merged.confirmed_elements)}, unconfirmed={len(merged.unconfirmed_elements)}")
    elif request.image:
        logger.info(f"Single-photo evaluate: session={redact_session_id(session_id)}")
        processed_image = process_image_base64(request.image)
        extraction = await vision_service.extract_elements(processed_image)
        store_extraction_result(session_id, extraction)
        elements = [
            {
                "id": e.id,
                "type": e.type,
                "position": e.position_relative_to_camera,
                "orientation": None,
                "confidence": e.confidence,
            }
            for e in extraction.elements
        ]
        logger.info(f"Single-photo complete: session={redact_session_id(session_id)}, elements={len(elements)}")
    else:
        raise HTTPException(status_code=422, detail="Either 'image' or 'images' must be provided")

    return EvaluateResponse(
        session_id=session_id,
        elements=elements,
        score=MOCK_SCORE,
    )