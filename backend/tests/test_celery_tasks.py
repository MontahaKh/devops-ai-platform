"""Tests for Celery task retry and terminal failure behavior."""
import pytest
from celery.exceptions import Retry

from app.workers import tasks


def test_task_retries_when_run_can_be_retried(monkeypatch: pytest.MonkeyPatch):
    def fail(_run_id: int):
        raise RuntimeError("temporary failure")

    monkeypatch.setattr(tasks, "execute_run", fail)
    monkeypatch.setattr(tasks, "prepare_run_retry", lambda *_: True)

    retry_calls: list[dict] = []

    def retry(**kwargs):
        retry_calls.append(kwargs)
        raise Retry("retry requested")

    monkeypatch.setattr(tasks.execute_run_task, "retry", retry)

    with pytest.raises(Retry):
        tasks.execute_run_task.run(42)
    assert retry_calls[0]["countdown"] == 2
    assert retry_calls[0]["max_retries"] == 10


def test_task_marks_run_failed_when_retries_are_exhausted(monkeypatch: pytest.MonkeyPatch):
    errors: list[str] = []

    def fail(_run_id: int):
        raise RuntimeError("permanent failure")

    monkeypatch.setattr(tasks, "execute_run", fail)
    monkeypatch.setattr(tasks, "prepare_run_retry", lambda *_: False)
    monkeypatch.setattr(tasks, "mark_run_failed", lambda _run_id, message: errors.append(message))

    with pytest.raises(RuntimeError, match="permanent failure"):
        tasks.execute_run_task.run(42)
    assert errors == ["permanent failure"]