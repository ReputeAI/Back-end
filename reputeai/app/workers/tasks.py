from datetime import datetime

from tenacity import retry, stop_after_attempt, wait_fixed

from ..db.session import SessionLocal
from ..models.integration import Integration
from ..models.review import Review
from ..models.org import Org
from ..services.integrations import get_provider
from ..services import ai as ai_service
from ..services.usage import log_usage
from ..core.security import decrypt_token
from .celery_app import celery_app


@celery_app.task
def example_task() -> str:
    return "ok"


@celery_app.task
def fetch_reviews(org_id: int, provider: str) -> int:
    integration: Integration | None
    with SessionLocal() as db:
        integration = (
            db.query(Integration)
            .filter(Integration.org_id == org_id, Integration.provider == provider)
            .first()
        )
        if integration is None:
            return 0

        token = decrypt_token(integration.access_token)

        @retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
        def _fetch() -> list[dict]:
            return get_provider(provider).fetch_reviews(token)

        reviews = _fetch()
        saved = 0
        for data in reviews:
            existing = (
                db.query(Review)
                .filter(
                    Review.org_id == org_id,
                    Review.platform == provider,
                    Review.external_id == data["external_id"],
                )
                .first()
            )
            if existing:
                existing.author = data.get("author")
                existing.rating = data.get("rating")
                existing.text = data.get("text")
                existing.lang = data.get("lang")
                existing.updated_at = data.get("updated_at", datetime.utcnow())
                existing.meta = data.get("metadata", {})
            else:
                db.add(
                    Review(
                        org_id=org_id,
                        platform=provider,
                        external_id=data["external_id"],
                        author=data.get("author"),
                        rating=data.get("rating"),
                        text=data.get("text"),
                        lang=data.get("lang"),
                        created_at=data.get("created_at", datetime.utcnow()),
                        updated_at=data.get("updated_at", datetime.utcnow()),
                        meta=data.get("metadata", {}),
                    )
                )
                saved += 1
        db.commit()
        return saved


@celery_app.task(rate_limit="5/m")
def batch_generate_replies(org_id: int, review_ids: list[int]) -> dict[int, list[str]]:
    results: dict[int, list[str]] = {}
    with SessionLocal() as db:
        org = db.query(Org).filter(Org.id == org_id).first()
        brand_voice = (org.settings or {}).get("brand_voice", {}) if org else {}
        for review_id in review_ids:
            review = (
                db.query(Review)
                .filter(Review.id == review_id, Review.org_id == org_id)
                .first()
            )
            if not review:
                continue
            suggestions = ai_service.suggest_replies(
                review.text,
                tone=brand_voice.get("tone", "friendly"),
                language=review.lang,
                brand_voice=brand_voice,
            )
            results[review_id] = suggestions
            log_usage(db, org_id)
    return results
