"""Authentication integration tests."""

from fastapi.testclient import TestClient


def test_register_and_login_user(client: TestClient):
    """Test registering and logging in a user."""
    register_response = client.post(
        "/auth/register",
        json={
            "username": "auth_user",
            "email": "auth_user@example.com",
            "password": "securepassword123",
        },
    )
    assert register_response.status_code == 201
    user_data = register_response.json()
    assert user_data["role"] == "user"

    login_response = client.post(
        "/auth/login",
        json={
            "username": "auth_user",
            "password": "securepassword123",
        },
    )
    assert login_response.status_code == 200
    payload = login_response.json()
    assert "access_token" in payload
    assert "refresh_token" in payload
    assert payload["token_type"] == "bearer"


def test_login_with_invalid_credentials(client: TestClient):
    """Test login fails invalid password."""
    client.post(
        "/auth/register",
        json={
            "username": "auth_user2",
            "email": "auth_user2@example.com",
            "password": "securepassword123",
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "username": "auth_user2",
            "password": "wrong_password",
        },
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]


def test_access_protected_route_requires_auth(client: TestClient):
    """Test protected route without token is rejected."""
    response = client.get("/users/me")
    assert response.status_code == 401


def test_access_protected_route_with_token(client: TestClient):
    """Test protected route with valid token is accepted."""
    register_response = client.post(
        "/auth/register",
        json={
            "username": "auth_user3",
            "email": "auth_user3@example.com",
            "password": "securepassword123",
        },
    )
    user_id = register_response.json()["id"]

    login_response = client.post(
        "/auth/login",
        json={
            "username": "auth_user3",
            "password": "securepassword123",
        },
    )
    token = login_response.json()["access_token"]

    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json()["id"] == user_id


def test_refresh_token(client: TestClient):
    """Test refresh token gives a new access token."""
    client.post(
        "/auth/register",
        json={
            "username": "auth_user4",
            "email": "auth_user4@example.com",
            "password": "securepassword123",
        },
    )

    login_response = client.post(
        "/auth/login",
        json={
            "username": "auth_user4",
            "password": "securepassword123",
        },
    )
    refresh_token = login_response.json()["refresh_token"]

    response = client.post(
        "/auth/refresh",
        json={"refresh_token": refresh_token},
    )
    assert response.status_code == 200
    payload = response.json()
    assert "access_token" in payload
    assert payload["token_type"] == "bearer"


def test_refresh_token_is_rotated_and_cannot_be_reused(client: TestClient):
    """Test that refresh token rotation revokes the previous refresh token."""
    client.post(
        "/auth/register",
        json={
            "username": "auth_rotation",
            "email": "auth_rotation@example.com",
            "password": "securepassword123",
        },
    )
    login_response = client.post(
        "/auth/login",
        json={"username": "auth_rotation", "password": "securepassword123"},
    )
    refresh_token = login_response.json()["refresh_token"]

    first_refresh = client.post(
        "/auth/refresh", json={"refresh_token": refresh_token}
    )
    assert first_refresh.status_code == 200

    reused_refresh = client.post(
        "/auth/refresh", json={"refresh_token": refresh_token}
    )
    assert reused_refresh.status_code == 401


def test_logout_blacklists_token(client: TestClient):
    """Test logout blacklists the token."""
    client.post(
        "/auth/register",
        json={
            "username": "auth_user5",
            "email": "auth_user5@example.com",
            "password": "securepassword123",
        },
    )

    login_response = client.post(
        "/auth/login",
        json={
            "username": "auth_user5",
            "password": "securepassword123",
        },
    )
    token = login_response.json()["access_token"]

    # Logout should work
    logout_response = client.post(
        "/auth/logout",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert logout_response.status_code == 200
    assert logout_response.json()["message"] == "Successfully logged out"

    # Using token after logout should fail
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401


def test_user_role_default(client: TestClient):
    """Test new users have default role 'user'."""
    response = client.post(
        "/auth/register",
        json={
            "username": "auth_user6",
            "email": "auth_user6@example.com",
            "password": "securepassword123",
        },
    )
    assert response.status_code == 201
    assert response.json()["role"] == "user"
