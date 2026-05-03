from fastapi import APIRouter

router = APIRouter(prefix="/v1")


@router.get("/health")
def health():
    return {"status": "ok"}