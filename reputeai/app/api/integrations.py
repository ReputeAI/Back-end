from fastapi import APIRouter

router = APIRouter(prefix="/integrations")


@router.get("/")
async def read_integrations() -> dict[str, str]:
    return {"message": "integrations"}
