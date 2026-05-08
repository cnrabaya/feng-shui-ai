import uuid
from fastapi import APIRouter, Request, HTTPException

from app.core.logger import get_logger, redact_session_id
from app.models.schemas import (
    EvaluateRequest,
    EvaluateResponse,
    MultiImageData,
    RoomGrid,
    Score,
    Issue,
)
from app.services.vision import vision_service
from app.services.merge import merge_service
from app.services.scoring import scoring_service
from app.services.layout import layout_service
from app.services.session import store_extraction_result, store_merged_result
from app.core.utils import process_image_base64

logger = get_logger("evaluate")

router = APIRouter(tags=["evaluate"])


@router.post("/evaluate", response_model=EvaluateResponse)
async def evaluate_room(request: EvaluateRequest, http_request: Request) -> EvaluateResponse:
    session_id = request.session_id or str(uuid.uuid4())
    dimensions = request.dimensions

    room_grid: RoomGrid | None = None
    
    if request.images:
        image_count = len(request.images)
        logger.info(f"Multi-photo evaluate: session={redact_session_id(session_id)}, images={image_count}, school={request.school}")
        processed_images = [
            MultiImageData(image=process_image_base64(img.image), direction=img.direction)
            for img in request.images
        ]
        extractions = await vision_service.extract_elements_batch(images=processed_images, dimensions=dimensions)
        merged = await merge_service.merge_results(extractions)

        if dimensions:
            logger.debug(f"Generating room grid for session={redact_session_id(session_id)}")
            grid = await layout_service.generate_grid(merged.model_dump_json(indent=2), dimensions)
            merged.room_grid = grid
            room_grid = grid

        store_merged_result(session_id, merged, school=request.school, dimensions=request.dimensions)
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
        logger.info(f"Multi-photo complete: session={redact_session_id(session_id)}, confirmed={len(merged.confirmed_elements)}, unconfirmed={len(merged.unconfirmed_elements)}, grid={'generated' if room_grid else 'skipped'}")

    elif request.image:
        logger.info(f"Single-photo evaluate: session={redact_session_id(session_id)}, school={request.school}")
        processed_image = process_image_base64(request.image)
        extraction = await vision_service.extract_elements(processed_image, dimensions=dimensions)

        if dimensions:
            logger.debug(f"Generating room grid for session={redact_session_id(session_id)}")
            grid = await layout_service.generate_grid(extraction.model_dump_json(indent=2), dimensions)
            room_grid = grid

        store_extraction_result(session_id, extraction, school=request.school, dimensions=request.dimensions)
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
        logger.info(f"Single-photo complete: session={redact_session_id(session_id)}, elements={len(elements)}, grid={'generated' if room_grid else 'skipped'}")

    else:
        raise HTTPException(status_code=422, detail="Either 'image' or 'images' must be provided")

    logger.info(f"Scoring with {request.school} school: session={redact_session_id(session_id)}")
    score_result = await scoring_service.score(
        elements=elements,
        school=request.school,
        dimensions=request.dimensions,
        birth_date=request.birth_date,
        kua_number=request.kua_number,
        building_date=request.building_date,
    )

    score_normalized = Score(
        total=score_result.get("total_score", score_result.get("total", 0)),
        chi_flow=str(score_result.get("chi_flow", "unknown")),
        breakdown=score_result.get("breakdown", {}),
        issues=[Issue(**issue) for issue in score_result.get("issues", [])],
        overall_assessment=score_result.get("overall_assessment"),
        school_specific=score_result.get("school_specific"),
    )

    return EvaluateResponse(
        session_id=session_id,
        elements=elements,
        score=score_normalized,
        room_grid=room_grid,
        dimensions=dimensions,
    )