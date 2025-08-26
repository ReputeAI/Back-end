from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..db.session import get_db
from ..models.org import Org
from ..models.review import Review
from ..services import ai as ai_service
from ..services.usage import log_usage
from ..workers.tasks import batch_generate_replies
from ..schemas.ai import (
    BatchSuggestRequest,
    SentimentRequest,
    SentimentResponse,
    SuggestReplyRequest,
    SuggestReplyResponse,
)


router = APIRouter(prefix="/orgs/{org_id}/ai")


@router.post("/sentiment", response_model=SentimentResponse)
def sentiment(org_id: int, body: SentimentRequest, db: Session = Depends(get_db)):
    result = ai_service.analyze_sentiment(body.text)
    log_usage(db, org_id)
    return result


@router.post("/suggest-reply", response_model=SuggestReplyResponse)
def suggest_reply(
    org_id: int, body: SuggestReplyRequest, db: Session = Depends(get_db)
):
    review = (
        db.query(Review)
        .filter(Review.id == body.review_id, Review.org_id == org_id)
        .first()
    )
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    org = db.query(Org).filter(Org.id == org_id).first()
    brand_voice = (org.settings or {}).get("brand_voice", {}) if org else {}
    suggestions = ai_service.suggest_replies(
        review.text,
        tone=body.tone or brand_voice.get("tone", "friendly"),
        language=body.language or review.lang,
        brand_voice=brand_voice,
    )
    log_usage(db, org_id)
    return SuggestReplyResponse(suggestions=suggestions)


@router.post("/batch-suggest")
def batch_suggest(org_id: int, body: BatchSuggestRequest):
    task = batch_generate_replies.delay(org_id=org_id, review_ids=body.review_ids)
    return {"job_id": task.id}

