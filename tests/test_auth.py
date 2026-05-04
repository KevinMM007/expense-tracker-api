from fastapi.testclient import TestClient


def test_register_creates_user(client: TestClient) -> None:
    r = client.post(
        "/api/v1/auth/register",
        json={"email": "alice@example.com", "password": "password123", "full_name": "Alice"},
    )
    assert r.status_code == 201
    body = r.json()
    assert body["email"] == "alice@example.com"
    assert body["full_name"] == "Alice"
    assert body["is_active"] is True
    assert "id" in body
    assert "hashed_password" not in body


def test_register_duplicate_email_returns_409(client: TestClient) -> None:
    payload = {"email": "dupe@example.com", "password": "password123"}
    assert client.post("/api/v1/auth/register", json=payload).status_code == 201
    r = client.post("/api/v1/auth/register", json=payload)
    assert r.status_code == 409


def test_register_rejects_short_password(client: TestClient) -> None:
    r = client.post(
        "/api/v1/auth/register",
        json={"email": "bob@example.com", "password": "short"},
    )
    assert r.status_code == 422


def test_login_returns_token(client: TestClient) -> None:
    client.post(
        "/api/v1/auth/register",
        json={"email": "login@example.com", "password": "password123"},
    )
    r = client.post(
        "/api/v1/auth/login",
        data={"username": "login@example.com", "password": "password123"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["token_type"] == "bearer"
    assert isinstance(body["access_token"], str) and len(body["access_token"]) > 20


def test_login_wrong_password_returns_401(client: TestClient) -> None:
    client.post(
        "/api/v1/auth/register",
        json={"email": "wrong@example.com", "password": "password123"},
    )
    r = client.post(
        "/api/v1/auth/login",
        data={"username": "wrong@example.com", "password": "WRONG_PASSWORD"},
    )
    assert r.status_code == 401


def test_me_requires_auth(client: TestClient) -> None:
    assert client.get("/api/v1/auth/me").status_code == 401


def test_me_returns_user(client: TestClient, auth_headers: dict[str, str]) -> None:
    r = client.get("/api/v1/auth/me", headers=auth_headers)
    assert r.status_code == 200
    assert r.json()["email"] == "tester@example.com"


def test_me_with_invalid_token(client: TestClient) -> None:
    r = client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer not-a-real-token"}
    )
    assert r.status_code == 401
