"""Smoke tests for the Mangum-wrapped Lambda handler.

We don't need to test FastAPI - that's covered by every other test module.
What we test here is that the Mangum integration is wired correctly:
events from API Gateway HTTP API v2 reach the FastAPI app and get a valid
Lambda response back.
"""

from __future__ import annotations

import json
from typing import Any


def _api_gw_v2_event(method: str, path: str, body: str | None = None) -> dict[str, Any]:
    """Build a minimal API Gateway HTTP API v2 event matching Mangum's expectations."""
    event: dict[str, Any] = {
        "version": "2.0",
        "routeKey": f"{method} {path}",
        "rawPath": path,
        "rawQueryString": "",
        "headers": {
            "accept": "application/json",
            "content-type": "application/json",
            "host": "test.execute-api.us-east-2.amazonaws.com",
        },
        "requestContext": {
            "accountId": "123456789012",
            "apiId": "test",
            "domainName": "test.execute-api.us-east-2.amazonaws.com",
            "http": {
                "method": method,
                "path": path,
                "protocol": "HTTP/1.1",
                "sourceIp": "127.0.0.1",
                "userAgent": "pytest",
            },
            "requestId": "test-request-id",
            "routeKey": f"{method} {path}",
            "stage": "$default",
            "time": "01/Jan/2026:00:00:00 +0000",
            "timeEpoch": 1735689600,
        },
        "isBase64Encoded": False,
    }
    if body is not None:
        event["body"] = body
    return event


def test_handler_is_importable_and_callable() -> None:
    from app.lambda_handler import handler

    assert callable(handler)


def test_handler_serves_root_endpoint() -> None:
    from app.lambda_handler import handler

    event = _api_gw_v2_event("GET", "/")
    response = handler(event, None)

    assert response["statusCode"] == 200
    body = json.loads(response["body"])
    assert body["status"] == "running"


def test_handler_serves_ping_endpoint() -> None:
    from app.lambda_handler import handler

    event = _api_gw_v2_event("GET", "/api/v1/ping")
    response = handler(event, None)

    assert response["statusCode"] == 200
    assert json.loads(response["body"]) == {"status": "ok"}


def test_handler_returns_401_on_protected_endpoint_without_token() -> None:
    """Verifies the auth middleware still runs through the Lambda path."""
    from app.lambda_handler import handler

    event = _api_gw_v2_event("GET", "/api/v1/auth/me")
    response = handler(event, None)

    assert response["statusCode"] == 401
