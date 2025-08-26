from fastapi import APIRouter

router = APIRouter(prefix="/usage")


@router.get("/")
async def read_usage() -> dict[str, str]:
    return {"message": "usage"}
