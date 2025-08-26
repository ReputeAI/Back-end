from fastapi import APIRouter

router = APIRouter(prefix="/orgs")


@router.get("/")
async def read_orgs() -> dict[str, str]:
    return {"message": "orgs"}
