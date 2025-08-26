from fastapi import APIRouter

router = APIRouter(prefix="/reviews")


@router.get("/")
async def read_reviews() -> dict[str, str]:
    return {"message": "reviews"}
