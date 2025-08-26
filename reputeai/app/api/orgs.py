from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db.session import get_db
from ..models.integration import Integration
from ..models.review import Review
from ..services.integrations import get_provider
from ..workers.tasks import fetch_reviews

router = APIRouter(prefix="/orgs")


@router.post("/{org_id}/integrations/{provider}/connect")
def start_connect(org_id: int, provider: str) -> dict[str, str]:
    url = get_provider(provider).get_authorization_url(org_id)
    return {"authorization_url": url}


@router.delete("/{org_id}/integrations/{provider}")
def delete_integration(org_id: int, provider: str, db: Session = Depends(get_db)) -> dict[str, str]:
    integration = db.query(Integration).filter_by(org_id=org_id, provider=provider).first()
    if not integration:
        raise HTTPException(status_code=404, detail="Integration not found")
    db.delete(integration)
    db.commit()
    return {"status": "deleted"}


@router.get("/{org_id}/reviews")
def list_reviews(
    org_id: int,
    platform: str | None = None,
    sentiment: str | None = None,
    rating_min: int | None = None,
    date_from: datetime | None = None,
    q: str | None = None,
    page: int = 1,
    size: int = 50,
    db: Session = Depends(get_db),
) -> list[Review]:
    query = db.query(Review).filter(Review.org_id == org_id)
    if platform:
        query = query.filter(Review.platform == platform)
    if sentiment:
        query = query.filter(Review.sentiment == sentiment)
    if rating_min is not None:
        query = query.filter(Review.rating >= rating_min)
    if date_from:
        query = query.filter(Review.created_at >= date_from)
    if q:
        query = query.filter(Review.text.ilike(f"%{q}%"))
    return query.offset((page - 1) * size).limit(size).all()


@router.post("/{org_id}/reviews/refresh")
def refresh_reviews(org_id: int, db: Session = Depends(get_db)) -> dict[str, str]:
    integrations = db.query(Integration).filter_by(org_id=org_id).all()
    for integration in integrations:
        fetch_reviews.delay(org_id=org_id, provider=integration.provider)
    return {"status": "enqueued"}
