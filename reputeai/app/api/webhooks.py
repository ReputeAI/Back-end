import json

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ..core.config import settings
from ..db.session import get_db
from ..models import Org
from ..services.billing import price_to_plan

try:  # pragma: no cover - optional
    import stripe
except Exception:  # pragma: no cover
    stripe = None  # type: ignore


if stripe is not None and settings.stripe_secret_key:
    stripe.api_key = settings.stripe_secret_key


router = APIRouter(prefix="/webhooks")


@router.post("/stripe")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)) -> dict[str, str]:
    if stripe is None:
        raise HTTPException(status_code=500, detail="Stripe not configured")
    payload = await request.body()
    sig = request.headers.get("stripe-signature")
    try:
        if settings.stripe_webhook_secret:
            event = stripe.Webhook.construct_event(
                payload, sig, settings.stripe_webhook_secret
            )
        else:  # pragma: no cover - no signature
            event = stripe.Event.construct_from(json.loads(payload), stripe.api_key)
    except Exception as exc:  # pragma: no cover - invalid payload
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    event_type = event["type"]
    data = event["data"]["object"]

    if event_type == "checkout.session.completed":
        org_id = int(data.get("client_reference_id", 0))
        customer_id = data.get("customer")
        plan = data.get("metadata", {}).get("plan", "FREE")
        org = db.get(Org, org_id)
        if org:
            org.plan = plan
            org.stripe_customer_id = customer_id
            db.commit()
    elif event_type in {"customer.subscription.updated", "customer.subscription.deleted"}:
        customer_id = data.get("customer")
        org = db.query(Org).filter(Org.stripe_customer_id == customer_id).first()
        if org:
            price_id = None
            items = data.get("items", {}).get("data", [])
            if items:
                price_id = items[0]["price"]["id"]
            org.plan = price_to_plan(price_id)
            db.commit()
    elif event_type == "invoice.paid":
        pass

    return {"status": "ok"}

