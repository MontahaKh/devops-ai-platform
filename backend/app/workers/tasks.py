"""Celery tasks for pipeline execution."""
from celery.exceptions import SoftTimeLimitExceeded

from app.services.execution import execute_run, mark_run_failed, prepare_run_retry
from app.workers.celery_app import celery_app


@celery_app.task(bind=True, name="app.workers.tasks.execute_run_task")
def execute_run_task(self, run_id: int) -> str:
    """Execute one pipeline run with timeout and bounded retries."""
    try:
        return execute_run(run_id)
    except SoftTimeLimitExceeded as exc:
        mark_run_failed(run_id, "Pipeline run timed out")
        raise exc
    except Exception as exc:
        if prepare_run_retry(run_id, str(exc)):
            raise self.retry(exc=exc, countdown=2, max_retries=10)
        mark_run_failed(run_id, str(exc))
        raise
