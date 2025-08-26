from fastapi import APIRouter

router = APIRouter(prefix="/auth")


@router.get("/")
async def read_auth() -> dict[str, str]:
    return {"message": "auth"}
