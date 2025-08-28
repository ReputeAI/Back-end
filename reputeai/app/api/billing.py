from fastapi import APIRouter, Depends

from ..dependencies import get_current_org
from ..models import Org
from ..services.billing import create_billing_portal_session, create_checkout_session


router = APIRouter(prefix="/billing")


@router.post("/checkout")
def checkout(
    body: dict[str, str],
    org: Org = Depends(get_current_org()),
) -> dict[str, str]:
    plan = body.get("plan", "").upper()
    url = create_checkout_session(org.id, plan)
    return {"url": url}


@router.get("/portal")
def portal(org: Org = Depends(get_current_org())) -> dict[str, str]:
    if not org.stripe_customer_id:
        return {"url": ""}
    url = create_billing_portal_session(org.stripe_customer_id)
    return {"url": url}

