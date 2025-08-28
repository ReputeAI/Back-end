from datetime import datetime

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from ..db.session import get_db
from ..models.integration import Integration
from ..models.review import Review
from ..models.reply import Reply
from ..services.integrations import get_provider
from ..services.replies import create_reply, send_reply
from ..workers.tasks import fetch_reviews
from ..schemas.reply import ReplyCreate, ReplyOut
from ..schemas.autoreply import (
    AutoReplySimulateRequest,
    AutoReplySimulateResponse,
)

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


@router.get("/{org_id}/reviews", response_model=None)
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
):
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


@router.post("/{org_id}/reviews/{review_id}/reply", response_model=ReplyOut)
def create_reply_endpoint(
    org_id: int,
    review_id: int,
    data: ReplyCreate,
    x_user_id: int | None = Header(None, alias="X-User-Id"),
    db: Session = Depends(get_db),
) -> Reply:
    return create_reply(db, org_id, review_id, data.text, data.is_auto, x_user_id)


@router.post("/{org_id}/reviews/{review_id}/send-reply", response_model=ReplyOut)
def send_reply_endpoint(
    org_id: int,
    review_id: int,
    x_user_id: int | None = Header(None, alias="X-User-Id"),
    db: Session = Depends(get_db),
) -> Reply:
    return send_reply(db, org_id, review_id, x_user_id)


@router.get("/{org_id}/replies", response_model=list[ReplyOut])
def list_replies(org_id: int, review_id: int | None = None, db: Session = Depends(get_db)):
    query = db.query(Reply).filter(Reply.org_id == org_id)
    if review_id:
        query = query.filter(Reply.review_id == review_id)
    return query.all()


@router.post("/{org_id}/autoreply/simulate", response_model=AutoReplySimulateResponse)
def autoreply_simulate(org_id: int, data: AutoReplySimulateRequest) -> AutoReplySimulateResponse:
    eligible = True
    if data.rating < data.min_rating:
        eligible = False
    if any(word.lower() in data.text.lower() for word in data.blacklist):
        eligible = False
    if not (
        data.office_hours_start <= data.timestamp.time() <= data.office_hours_end
    ):
        eligible = False
    return AutoReplySimulateResponse(eligible=eligible)
