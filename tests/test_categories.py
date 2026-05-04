from fastapi.testclient import TestClient


def test_list_empty(client: TestClient, auth_headers: dict[str, str]) -> None:
    r = client.get("/api/v1/categories", headers=auth_headers)
    assert r.status_code == 200
    assert r.json() == []


def test_create_and_list(client: TestClient, auth_headers: dict[str, str]) -> None:
    r = client.post("/api/v1/categories", json={"name": "Food"}, headers=auth_headers)
    assert r.status_code == 201
    body = r.json()
    assert body["name"] == "Food"

    r = client.get("/api/v1/categories", headers=auth_headers)
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_create_duplicate_name_returns_409(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    client.post("/api/v1/categories", json={"name": "Food"}, headers=auth_headers)
    r = client.post("/api/v1/categories", json={"name": "Food"}, headers=auth_headers)
    assert r.status_code == 409


def test_get_404_on_other_user(client: TestClient) -> None:
    # User A creates a category
    client.post(
        "/api/v1/auth/register",
        json={"email": "a@a.com", "password": "password123"},
    )
    a_token = client.post(
        "/api/v1/auth/login", data={"username": "a@a.com", "password": "password123"}
    ).json()["access_token"]
    a_headers = {"Authorization": f"Bearer {a_token}"}
    cat = client.post(
        "/api/v1/categories", json={"name": "Travel"}, headers=a_headers
    ).json()

    # User B tries to read it
    client.post(
        "/api/v1/auth/register",
        json={"email": "b@b.com", "password": "password123"},
    )
    b_token = client.post(
        "/api/v1/auth/login", data={"username": "b@b.com", "password": "password123"}
    ).json()["access_token"]
    b_headers = {"Authorization": f"Bearer {b_token}"}

    r = client.get(f"/api/v1/categories/{cat['id']}", headers=b_headers)
    assert r.status_code == 404


def test_update_category(client: TestClient, auth_headers: dict[str, str]) -> None:
    cat = client.post(
        "/api/v1/categories", json={"name": "Food"}, headers=auth_headers
    ).json()
    r = client.patch(
        f"/api/v1/categories/{cat['id']}",
        json={"name": "Groceries"},
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert r.json()["name"] == "Groceries"


def test_delete_category(client: TestClient, auth_headers: dict[str, str]) -> None:
    cat = client.post(
        "/api/v1/categories", json={"name": "Food"}, headers=auth_headers
    ).json()
    r = client.delete(f"/api/v1/categories/{cat['id']}", headers=auth_headers)
    assert r.status_code == 204
    r = client.get(f"/api/v1/categories/{cat['id']}", headers=auth_headers)
    assert r.status_code == 404


def test_categories_require_auth(client: TestClient) -> None:
    assert client.get("/api/v1/categories").status_code == 401
    assert client.post("/api/v1/categories", json={"name": "x"}).status_code == 401
