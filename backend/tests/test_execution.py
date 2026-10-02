"""Tests for the pipeline execution lifecycle."""
import subprocess

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.services.execution import execute_run_in_session


def create_run(client: TestClient) -> tuple[int, dict]:
    client.post(
        "/auth/register",
        json={
            "username": "execution_user",
            "email": "execution@example.com",
            "password": "securepassword123",
        },
    )
    token = client.post(
        "/auth/login",
        json={"username": "execution_user", "password": "securepassword123"},
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    project = client.post(
        "/projects", headers=headers, json={"name": "Execution Project"}
    ).json()
    pipeline = client.post(
        "/pipelines",
        headers=headers,
        json={"name": "Execution Pipeline", "project_id": project["id"]},
    ).json()
    run = client.post(
        "/runs", headers=headers, json={"pipeline_id": pipeline["id"]}
    ).json()
    return run["id"], headers


def test_run_has_correlation_id_and_worker_transitions_to_success(
    client: TestClient, db_session: Session
):
    run_id, headers = create_run(client)
    initial = client.get(f"/runs/{run_id}", headers=headers).json()
    assert initial["status"] == "pending"
    assert len(initial["correlation_id"]) == 36
    assert initial["retry_count"] == 0

    assert execute_run_in_session(db_session, run_id) == "success"
    completed = client.get(f"/runs/{run_id}", headers=headers).json()
    assert completed["status"] == "success"
    assert completed["started_at"] is not None
    assert completed["finished_at"] is not None


def test_pending_run_can_be_cancelled(client: TestClient):
    run_id, headers = create_run(client)
    response = client.post(f"/runs/{run_id}/cancel", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "cancelled"

    second_cancel = client.post(f"/runs/{run_id}/cancel", headers=headers)
    assert second_cancel.status_code == 409


def test_terminal_run_transitions_are_rejected(client: TestClient):
    run_id, headers = create_run(client)
    assert client.put(f"/runs/{run_id}", headers=headers, json={"status": "success"}).status_code == 200
    success_to_running = client.put(
        f"/runs/{run_id}", headers=headers, json={"status": "running"}
    )
    assert success_to_running.status_code == 409

    cancelled_run_id, cancelled_headers = create_run(client)
    assert client.post(
        f"/runs/{cancelled_run_id}/cancel", headers=cancelled_headers
    ).status_code == 200
    cancelled_to_success = client.put(
        f"/runs/{cancelled_run_id}",
        headers=cancelled_headers,
        json={"status": "success"},
    )
    assert cancelled_to_success.status_code == 409


def test_terraform_validation_persists_command_output(
    client: TestClient, db_session: Session, monkeypatch: pytest.MonkeyPatch
):
    run_id, headers = create_run(client)
    generated = client.post(
        "/generated-files",
        headers=headers,
        json={
            "run_id": run_id,
            "file_type": "terraform",
            "path": "main.tf",
            "content": 'terraform { required_version = ">= 1.0.0" }',
        },
    )
    assert generated.status_code == 201

    calls: list[list[str]] = []

    def fake_run(command, **kwargs):
        calls.append(command)
        return subprocess.CompletedProcess(command, 0, "terraform stdout", "terraform stderr")

    monkeypatch.setattr("app.services.execution.shutil.which", lambda _: "terraform")
    monkeypatch.setattr("app.services.execution.subprocess.run", fake_run)

    assert execute_run_in_session(db_session, run_id) == "success"
    validations = client.get("/validations", headers=headers).json()
    assert len(validations) == 1
    assert validations[0]["status"] == "success"
    assert validations[0]["stdout"] == "terraform stdout\nterraform stdout\nterraform stdout"
    assert validations[0]["exit_code"] == 0
    assert len(calls) == 3


def test_run_is_executed_only_after_files_are_added(
    client: TestClient,
    db_session: Session,
    monkeypatch: pytest.MonkeyPatch,
):
    run_id, headers = create_run(client)
    assert client.get(f"/runs/{run_id}", headers=headers).json()["status"] == "pending"
    assert client.post(f"/runs/{run_id}/execute", headers=headers).status_code == 409

    generated = client.post(
        "/generated-files",
        headers=headers,
        json={
            "run_id": run_id,
            "file_type": "terraform",
            "path": "main.tf",
            "content": 'terraform { required_version = ">= 1.0.0" }',
        },
    )
    assert generated.status_code == 201

    monkeypatch.setattr("app.routers.run.settings.task_queue_enabled", False)
    monkeypatch.setattr("app.services.execution.shutil.which", lambda _: "terraform")
    monkeypatch.setattr(
        "app.services.execution.subprocess.run",
        lambda command, **kwargs: subprocess.CompletedProcess(command, 0, "", ""),
    )

    response = client.post(f"/runs/{run_id}/execute", headers=headers)
    assert response.status_code == 200
    assert response.json()["status"] == "success"
