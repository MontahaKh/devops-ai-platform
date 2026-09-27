"""Tests for the pipeline execution lifecycle."""
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
