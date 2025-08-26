from celery import Celery

from ..core.config import settings

celery_app = Celery("reputeai", broker=settings.redis_url)
