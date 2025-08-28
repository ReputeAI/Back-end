from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..models import AuditLog, Integration, Reply, Review
from .integrations import get_provider


def create_reply(
    db: Session,
    org_id: int,
    review_id: int,
    text: str,
    is_auto: bool,
    user_id: int | None,
) -> Reply:
    review = db.query(Review).filter_by(id=review_id, org_id=org_id).first()
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    reply = Reply(
        org_id=org_id,
        review_id=review_id,
        text=text,
        is_auto=is_auto,
        status="draft",
    )
    db.add(reply)
    db.flush()
    log = AuditLog(
        org_id=org_id,
        user_id=user_id,
        action="create_reply",
        payload={"reply_id": reply.id, "text": text},
    )
    db.add(log)
    db.commit()
    db.refresh(reply)
    return reply


def send_reply(db: Session, org_id: int, review_id: int, user_id: int | None) -> Reply:
    reply = (
        db.query(Reply)
        .filter_by(org_id=org_id, review_id=review_id)
        .order_by(Reply.id.desc())
        .first()
    )
    if reply is None:
        raise HTTPException(status_code=404, detail="Reply not found")
    review = db.query(Review).filter_by(id=review_id, org_id=org_id).first()
    if review is None:
        raise HTTPException(status_code=404, detail="Review not found")
    integration = (
        db.query(Integration)
        .filter_by(org_id=org_id, provider=review.platform)
        .first()
    )
    if integration is None:
        raise HTTPException(status_code=400, detail="Integration not found")
    provider = get_provider(review.platform)
    success = False
    try:
        success = provider.post_reply(
            integration.access_token, {"external_id": review.external_id}, reply.text
        )
    except Exception:
        success = False
    reply.status = "sent"
    if success:
        reply.platform_status = "posted"
        reply.posted_at = datetime.utcnow()
    else:
        reply.platform_status = "failed"
    log = AuditLog(
        org_id=org_id,
        user_id=user_id,
        action="send_reply",
        payload={"reply_id": reply.id, "success": success},
    )
    db.add(log)
    db.commit()
    db.refresh(reply)
    return reply
