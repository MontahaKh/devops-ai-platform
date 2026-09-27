"""Integration tests for secured pipeline execution domain entities."""
from datetime import datetime, timezone
from fastapi.testclient import TestClient


def create_domain_setup(client: TestClient) -> tuple[int, dict]:
    client.post(
        "/auth/register",
        json={"username": "domain_user", "email": "domain@example.com", "password": "securepassword123"},
    )
    token = client.post(
        "/auth/login", json={"username": "domain_user", "password": "securepassword123"}
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    project = client.post("/projects", headers=headers, json={"name": "Domain Project"}).json()
    return project["id"], headers


def test_pipeline_run_validation_deployment_and_file_flow(client: TestClient):
    project_id, headers = create_domain_setup(client)
    pipeline = client.post(
        "/pipelines", headers=headers,
        json={"name": "Infrastructure Pipeline", "project_id": project_id, "definition": {"steps": ["validate", "deploy"]}},
    )
    assert pipeline.status_code == 201
    run = client.post("/runs", headers=headers, json={"pipeline_id": pipeline.json()["id"]})
    assert run.status_code == 201
    run_id = run.json()["id"]
    assert client.post(
        "/validations", headers=headers,
        json={"run_id": run_id, "validation_type": "terraform_validate", "status": "success", "message": "Valid", "executed_at": datetime.now(timezone.utc).isoformat()},
    ).status_code == 201
    assert client.post(
        "/deployments", headers=headers,
        json={"run_id": run_id, "environment": "staging", "cloud_provider": "aws"},
    ).status_code == 201
    assert client.post(
        "/generated-files", headers=headers,
        json={"run_id": run_id, "file_type": "terraform", "path": "main.tf", "content": "resource \"aws_s3_bucket\" \"example\" {}"},
    ).status_code == 201
    assert client.put(f"/runs/{run_id}", headers=headers, json={"status": "success"}).status_code == 200


def test_domain_routes_require_authentication(client: TestClient):
    assert client.get("/pipelines").status_code == 401
    assert client.get("/runs").status_code == 401
    assert client.get("/validations").status_code == 401
    assert client.get("/deployments").status_code == 401
    assert client.get("/generated-files").status_code == 401
