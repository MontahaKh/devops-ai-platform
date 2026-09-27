"""Integration tests for secured user routes."""
from fastapi.testclient import TestClient


def register_and_login(client: TestClient, username: str = "john_doe") -> tuple[dict, dict]:
    user = client.post(
        "/auth/register",
        json={"username": username, "email": f"{username}@example.com", "password": "securepassword123"},
    ).json()
    token = client.post(
        "/auth/login", json={"username": username, "password": "securepassword123"}
    ).json()["access_token"]
    return user, {"Authorization": f"Bearer {token}"}


def test_user_creation_and_login_use_real_password_hash(client: TestClient):
    user, headers = register_and_login(client)
    response = client.get(f"/users/{user['id']}", headers=headers)
    assert response.status_code == 200
    assert "password" not in response.json()


def test_user_routes_require_authentication(client: TestClient):
    assert client.get("/users").status_code == 401
    assert client.get("/users/9999").status_code == 401
    assert client.put("/users/9999", json={"username": "changed"}).status_code == 401
    assert client.delete("/users/9999").status_code == 401


def test_user_can_update_own_profile(client: TestClient):
    user, headers = register_and_login(client)
    response = client.put(
        f"/users/{user['id']}", headers=headers,
        json={"username": "updated_user", "email": "updated@example.com"},
    )
    assert response.status_code == 200
    assert response.json()["username"] == "updated_user"


def test_updated_password_can_be_used_for_login(client: TestClient):
    user, headers = register_and_login(client, "password_user")
    response = client.put(
        f"/users/{user['id']}",
        headers=headers,
        json={"password": "newsecurepassword123"},
    )
    assert response.status_code == 200
    login_response = client.post(
        "/auth/login",
        json={"username": "password_user", "password": "newsecurepassword123"},
    )
    assert login_response.status_code == 200


def test_user_cannot_manage_another_user(client: TestClient):
    first_user, first_headers = register_and_login(client, "first_user")
    second_user, _ = register_and_login(client, "second_user")
    assert client.get(f"/users/{second_user['id']}", headers=first_headers).status_code == 403
    assert client.put(
        f"/users/{second_user['id']}", headers=first_headers,
        json={"username": "hacked_user"},
    ).status_code == 403


def test_regular_user_cannot_create_or_list_users(client: TestClient):
    _, headers = register_and_login(client)
    payload = {"username": "another_user", "email": "another@example.com", "password": "securepassword123"}
    assert client.post("/users", headers=headers, json=payload).status_code == 403
    assert client.get("/users", headers=headers).status_code == 403


def test_regular_user_cannot_delete_account(client: TestClient):
    user, headers = register_and_login(client)
    assert client.delete(f"/users/{user['id']}", headers=headers).status_code == 403
