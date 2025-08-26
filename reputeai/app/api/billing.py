from fastapi import APIRouter

router = APIRouter(prefix="/billing")


@router.get("/")
async def read_billing() -> dict[str, str]:
    return {"message": "billing"}
