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
        score=Score(
            total=0,
            breakdown=ScoreBreakdown(),
            issues=[],
            chi_flow="unknown",
        ),
    )