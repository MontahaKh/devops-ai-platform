"""Celery application configured with Redis as broker and result backend."""
from celery import Celery

from app.core.config import settings


celery_app = Celery(
    "devops_ai_platform",
    broker=settings.redis_url,
    backend=settings.redis_url,
)
celery_app.conf.update(
    task_track_started=True,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_time_limit=settings.run_timeout_seconds,
    task_soft_time_limit=max(settings.run_timeout_seconds - 5, 1),
    result_expires=3600,
)

# Import tasks so Celery discovers them when the worker starts.
celery_app.autodiscover_tasks(["app.workers"])
