from decimal import Decimal

from fastapi.testclient import TestClient


def _seed(client: TestClient, headers: dict[str, str]) -> dict:
    food = client.post(
        "/api/v1/categories", json={"name": "Food"}, headers=headers
    ).json()["id"]
    travel = client.post(
        "/api/v1/categories", json={"name": "Travel"}, headers=headers
    ).json()["id"]
    rows = [
        ("2026-04-10", food, "10.00"),
        ("2026-05-01", food, "20.00"),
        ("2026-05-15", food, "5.00"),
        ("2026-05-20", travel, "100.00"),
        ("2025-12-01", travel, "50.00"),
    ]
    for d, c, a in rows:
        client.post(
            "/api/v1/expenses",
            json={"amount": a, "spent_on": d, "category_id": c},
            headers=headers,
        )
    return {"food": food, "travel": travel}


def test_total_no_filters(client: TestClient, auth_headers: dict[str, str]) -> None:
    _seed(client, auth_headers)
    r = client.get("/api/v1/reports/total", headers=auth_headers)
    assert r.status_code == 200
    assert Decimal(r.json()["total"]) == Decimal("185.00")


def test_total_with_date_range(client: TestClient, auth_headers: dict[str, str]) -> None:
    _seed(client, auth_headers)
    r = client.get(
        "/api/v1/reports/total",
        params={"date_from": "2026-05-01", "date_to": "2026-05-31"},
        headers=auth_headers,
    )
    assert Decimal(r.json()["total"]) == Decimal("125.00")


def test_by_category(client: TestClient, auth_headers: dict[str, str]) -> None:
    _seed(client, auth_headers)
    r = client.get("/api/v1/reports/by-category", headers=auth_headers)
    assert r.status_code == 200
    rows = {row["category_name"]: Decimal(row["total"]) for row in r.json()}
    assert rows == {"Food": Decimal("35.00"), "Travel": Decimal("150.00")}


def test_by_month_for_year(client: TestClient, auth_headers: dict[str, str]) -> None:
    _seed(client, auth_headers)
    r = client.get(
        "/api/v1/reports/by-month", params={"year": 2026}, headers=auth_headers
    )
    assert r.status_code == 200
    by_month = {(row["year"], row["month"]): Decimal(row["total"]) for row in r.json()}
    assert by_month == {(2026, 4): Decimal("10.00"), (2026, 5): Decimal("125.00")}


def test_reports_require_auth(client: TestClient) -> None:
    assert client.get("/api/v1/reports/total").status_code == 401
    assert client.get("/api/v1/reports/by-category").status_code == 401
    assert client.get("/api/v1/reports/by-month").status_code == 401
