from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..core.config import settings
from ..models import Org, Usage


PLAN_LIMITS = {
    "FREE": {
        "reviews_fetched": settings.free_reviews_fetched_limit,
        "ai_suggestions": settings.free_ai_suggestions_limit,
        "auto_replies": settings.free_auto_replies_limit,
        "connected_locations": settings.free_connected_locations_limit,
    },
    "PRO": {
        "reviews_fetched": settings.pro_reviews_fetched_limit,
        "ai_suggestions": settings.pro_ai_suggestions_limit,
        "auto_replies": settings.pro_auto_replies_limit,
        "connected_locations": settings.pro_connected_locations_limit,
    },
    "BUSINESS": {
        "reviews_fetched": settings.business_reviews_fetched_limit,
        "ai_suggestions": settings.business_ai_suggestions_limit,
        "auto_replies": settings.business_auto_replies_limit,
        "connected_locations": settings.business_connected_locations_limit,
    },
}


def _get_or_create_usage(db: Session, org_id: int) -> Usage:
    month = datetime.utcnow().strftime("%Y-%m")
    usage = (
        db.query(Usage)
        .filter(Usage.org_id == org_id, Usage.month == month)
        .first()
    )
    if usage is None:
        usage = Usage(org_id=org_id, month=month)
        db.add(usage)
        db.commit()
        db.refresh(usage)
    return usage


def get_plan_limits(plan: str) -> dict[str, int]:
    return PLAN_LIMITS.get(plan.upper(), PLAN_LIMITS["FREE"])


def get_usage(db: Session, org_id: int) -> dict[str, int]:
    usage = _get_or_create_usage(db, org_id)
    return {
        "reviews_fetched": usage.reviews_fetched,
        "ai_suggestions": usage.ai_suggestions,
        "auto_replies": usage.auto_replies,
        "connected_locations": usage.connected_locations,
    }


def log_usage(db: Session, org_id: int, metric: str, amount: int = 1) -> None:
    org = db.get(Org, org_id)
    if org is None:
        return
    usage = _get_or_create_usage(db, org_id)
    limits = get_plan_limits(org.plan)
    current = getattr(usage, metric)
    limit = limits[metric]
    if current + amount > limit:
        remaining = limit - current
        raise HTTPException(
            status_code=402,
            detail={"code": "limit_exceeded", "remaining": {metric: max(0, remaining)}},
        )
    setattr(usage, metric, current + amount)
    db.commit()
