"""Lifecycle transition and timestamp validation helpers."""
from datetime import datetime, timezone


RUN_TRANSITIONS = {
    "pending": {"pending", "running", "success", "failed", "cancelled"},
    "running": {"running", "success", "failed", "cancelled"},
    "success": {"success"},
    "failed": {"failed", "pending"},
    "cancelled": {"cancelled"},
}

RESOURCE_TRANSITIONS = {
    "pending": {"pending", "running", "success", "failed", "cancelled"},
    "running": {"running", "success", "failed", "cancelled"},
    "success": {"success"},
    "failed": {"failed", "pending"},
    "cancelled": {"cancelled"},
}


def ensure_run_transition(current: str, target: str) -> None:
    if target not in RUN_TRANSITIONS.get(current, set()):
        raise ValueError(f"Invalid run status transition: {current} -> {target}")


def ensure_resource_transition(current: str, target: str) -> None:
    if target not in RESOURCE_TRANSITIONS.get(current, set()):
        raise ValueError(f"Invalid resource status transition: {current} -> {target}")


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def ensure_timestamp_order(
    started_at: datetime | None, finished_at: datetime | None
) -> None:
    if not started_at or not finished_at:
        return
    started = started_at.replace(tzinfo=timezone.utc) if started_at.tzinfo is None else started_at
    finished = finished_at.replace(tzinfo=timezone.utc) if finished_at.tzinfo is None else finished_at
    if finished < started:
        raise ValueError("finished_at must be greater than or equal to started_at")