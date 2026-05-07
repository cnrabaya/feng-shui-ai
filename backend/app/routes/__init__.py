from fastapi import APIRouter

from app.routes.evaluate import router as evaluate_router
from app.routes.suggest import router as suggest_router
from app.routes.elements import router as elements_router
from app.routes.score import router as score_router

router = APIRouter(prefix="/v1")

router.include_router(evaluate_router)
router.include_router(suggest_router)
router.include_router(elements_router)
router.include_router(score_router)


@router.get("/health")
def health():
    return {"status": "ok"}