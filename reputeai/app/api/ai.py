from fastapi import APIRouter

router = APIRouter(prefix="/ai")


@router.get("/")
async def read_ai() -> dict[str, str]:
    return {"message": "ai"}
