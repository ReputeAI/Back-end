from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..dependencies import get_current_org
from ..db.session import get_db
from ..models import Org
from ..services.usage import get_plan_limits, get_usage


router = APIRouter(prefix="/usage")


@router.get("/")
def read_usage(
    org: Org = Depends(get_current_org()),
    db: Session = Depends(get_db),
) -> dict[str, dict[str, int]]:
    usage = get_usage(db, org.id)
    limits = get_plan_limits(org.plan)
    return {"plan": org.plan, "usage": usage, "limits": limits}

