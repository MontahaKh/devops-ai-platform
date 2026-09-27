"""Integration tests for secured Project routes."""
from fastapi.testclient import TestClient


def create_user(client: TestClient, username: str = "project_user") -> tuple[dict, dict]:
    user = client.post(
        "/auth/register",
        json={"username": username, "email": f"{username}@example.com", "password": "securepassword123"},
    ).json()
    token = client.post(
        "/auth/login", json={"username": username, "password": "securepassword123"}
    ).json()["access_token"]
    return user, {"Authorization": f"Bearer {token}"}


def create_project(client: TestClient, headers: dict, name: str = "DevOps Platform") -> dict:
    response = client.post(
        "/projects", headers=headers,
        json={"name": name, "description": "AI-powered DevOps platform"},
    )
    assert response.status_code == 201
    return response.json()


def test_project_crud_for_owner(client: TestClient):
    _, headers = create_user(client)
    project = create_project(client, headers)
    project_id = project["id"]
    assert client.get("/projects", headers=headers).json()[0]["id"] == project_id
    assert client.get(f"/projects/{project_id}", headers=headers).status_code == 200
    response = client.put(f"/projects/{project_id}", headers=headers, json={"name": "Updated Project"})
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Project"
    assert client.delete(f"/projects/{project_id}", headers=headers).status_code == 204


def test_project_routes_require_authentication(client: TestClient):
    assert client.get("/projects").status_code == 401
    assert client.post("/projects", json={"name": "Private"}).status_code == 401


def test_user_cannot_access_another_users_project(client: TestClient):
    _, first_headers = create_user(client, "first_project_user")
    _, second_headers = create_user(client, "second_project_user")
    project_id = create_project(client, first_headers)["id"]
    assert client.get(f"/projects/{project_id}", headers=second_headers).status_code == 403
    assert client.put(
        f"/projects/{project_id}", headers=second_headers, json={"name": "Hacked"}
    ).status_code == 403


def test_project_ignores_caller_owner_parameter(client: TestClient):
    _, headers = create_user(client)
    response = client.post("/projects?owner_id=9999", headers=headers, json={"name": "Project"})
    assert response.status_code == 201
    assert response.json()["owner_id"] != 9999
    assert client.get("/projects/9999", headers=headers).status_code == 404
