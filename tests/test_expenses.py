from fastapi.testclient import TestClient


def _create_category(client: TestClient, headers: dict[str, str], name: str = "Food") -> int:
    return client.post("/api/v1/categories", json={"name": name}, headers=headers).json()["id"]


def test_create_expense(client: TestClient, auth_headers: dict[str, str]) -> None:
    cat_id = _create_category(client, auth_headers)
    r = client.post(
        "/api/v1/expenses",
        json={
            "amount": "12.50",
            "description": "Lunch",
            "spent_on": "2026-05-01",
            "category_id": cat_id,
        },
        headers=auth_headers,
    )
    assert r.status_code == 201
    body = r.json()
    assert body["amount"] == "12.50"
    assert body["description"] == "Lunch"


def test_create_expense_with_other_users_category_fails(client: TestClient) -> None:
    client.post(
        "/api/v1/auth/register", json={"email": "a@a.com", "password": "password123"}
    )
    a_token = client.post(
        "/api/v1/auth/login", data={"username": "a@a.com", "password": "password123"}
    ).json()["access_token"]
    a_headers = {"Authorization": f"Bearer {a_token}"}
    a_cat = _create_category(client, a_headers, "A's category")

    client.post(
        "/api/v1/auth/register", json={"email": "b@b.com", "password": "password123"}
    )
    b_token = client.post(
        "/api/v1/auth/login", data={"username": "b@b.com", "password": "password123"}
    ).json()["access_token"]
    b_headers = {"Authorization": f"Bearer {b_token}"}

    r = client.post(
        "/api/v1/expenses",
        json={"amount": "1.00", "spent_on": "2026-05-01", "category_id": a_cat},
        headers=b_headers,
    )
    assert r.status_code == 400


def test_list_expenses_with_filters(client: TestClient, auth_headers: dict[str, str]) -> None:
    food = _create_category(client, auth_headers, "Food")
    travel = _create_category(client, auth_headers, "Travel")
    for date_, cat, amount in [
        ("2026-04-01", food, "10.00"),
        ("2026-05-01", food, "20.00"),
        ("2026-05-15", travel, "100.00"),
    ]:
        client.post(
            "/api/v1/expenses",
            json={"amount": amount, "spent_on": date_, "category_id": cat},
            headers=auth_headers,
        )

    r = client.get(
        "/api/v1/expenses",
        params={"category_id": food},
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert len(r.json()) == 2

    r = client.get(
        "/api/v1/expenses",
        params={"date_from": "2026-05-01", "date_to": "2026-05-31"},
        headers=auth_headers,
    )
    assert len(r.json()) == 2


def test_update_and_delete_expense(client: TestClient, auth_headers: dict[str, str]) -> None:
    cat = _create_category(client, auth_headers)
    exp = client.post(
        "/api/v1/expenses",
        json={"amount": "5.00", "spent_on": "2026-05-01", "category_id": cat},
        headers=auth_headers,
    ).json()

    r = client.patch(
        f"/api/v1/expenses/{exp['id']}",
        json={"amount": "7.50", "description": "updated"},
        headers=auth_headers,
    )
    assert r.status_code == 200
    assert r.json()["amount"] == "7.50"
    assert r.json()["description"] == "updated"

    r = client.delete(f"/api/v1/expenses/{exp['id']}", headers=auth_headers)
    assert r.status_code == 204
    assert client.get(f"/api/v1/expenses/{exp['id']}", headers=auth_headers).status_code == 404


def test_expense_negative_amount_rejected(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    cat = _create_category(client, auth_headers)
    r = client.post(
        "/api/v1/expenses",
        json={"amount": "-5.00", "spent_on": "2026-05-01", "category_id": cat},
        headers=auth_headers,
    )
    assert r.status_code == 422
