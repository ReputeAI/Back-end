from typing import Optional

from fastapi import HTTPException

from ..core.config import settings

try:  # pragma: no cover - optional dependency
    import stripe
except Exception:  # pragma: no cover - stripe not installed
    stripe = None  # type: ignore


if stripe is not None and settings.stripe_secret_key:
    stripe.api_key = settings.stripe_secret_key


PRICE_IDS = {
    "FREE": settings.stripe_price_free,
    "PRO": settings.stripe_price_pro,
    "BUSINESS": settings.stripe_price_business,
}


def _require_stripe() -> None:
    if stripe is None or settings.stripe_secret_key is None:
        raise HTTPException(status_code=500, detail="Stripe not configured")


def create_checkout_session(org_id: int, plan: str) -> str:
    _require_stripe()
    price_id = PRICE_IDS.get(plan.upper())
    if not price_id:
        raise HTTPException(status_code=400, detail="Unknown plan")
    session = stripe.checkout.Session.create(
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url=f"{settings.frontend_url}/billing/success?session_id={{CHECKOUT_SESSION_ID}}",
        cancel_url=f"{settings.frontend_url}/billing/cancel",
        client_reference_id=org_id,
        metadata={"plan": plan.upper()},
    )
    return session.url


def create_billing_portal_session(customer_id: str) -> str:
    _require_stripe()
    session = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=f"{settings.frontend_url}/billing",
    )
    return session.url


def price_to_plan(price_id: Optional[str]) -> str:
    for plan, pid in PRICE_IDS.items():
        if pid == price_id:
            return plan
    return "FREE"
