from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from ..core.rate_limit import limiter
from ..db.session import get_db
from ..dependencies import get_current_org
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


router = APIRouter(prefix="/ai")


@router.post("/sentiment", response_model=SentimentResponse)
@limiter.limit("30/minute")
def sentiment(
    request: Request,
    body: SentimentRequest,
    org: Org = Depends(get_current_org()),
    db: Session = Depends(get_db),
):
    result = ai_service.analyze_sentiment(body.text)
    log_usage(db, org.id, "ai_suggestions")
    return result


@router.post("/suggest-reply", response_model=SuggestReplyResponse)
@limiter.limit("30/minute")
def suggest_reply(
    request: Request,
    body: SuggestReplyRequest,
    org: Org = Depends(get_current_org()),
    db: Session = Depends(get_db),
):
    review = (
        db.query(Review)
        .filter(Review.id == body.review_id, Review.org_id == org.id)
        .first()
    )
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    brand_voice = (org.settings or {}).get("brand_voice", {}) if org else {}
    suggestions = ai_service.suggest_replies(
        review.text,
        tone=body.tone or brand_voice.get("tone", "friendly"),
        language=body.language or review.lang,
        brand_voice=brand_voice,
    )
    log_usage(db, org.id, "ai_suggestions")
    return SuggestReplyResponse(suggestions=suggestions)


@router.post("/batch-suggest")
@limiter.limit("30/minute")
def batch_suggest(
    request: Request,
    body: BatchSuggestRequest,
    org: Org = Depends(get_current_org()),
):
    task = batch_generate_replies.delay(org_id=org.id, review_ids=body.review_ids)
    return {"job_id": task.id}

