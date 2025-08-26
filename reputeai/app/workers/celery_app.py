from celery import Celery

from ..core.config import settings

celery_app = Celery("reputeai", broker=settings.redis_url)
celery_app.conf.task_always_eager = True
