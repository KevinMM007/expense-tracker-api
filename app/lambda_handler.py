"""AWS Lambda entry point.

Mangum adapts ASGI apps (FastAPI) to Lambda's event-driven invocation model.
The same ``app.main:app`` instance that uvicorn serves locally is what we
hand to Mangum here - one app, two deployment targets (Render + AWS).

On Lambda cold start, we also run `alembic upgrade head` to keep the RDS
schema in sync with the application's models. Alembic upgrades are
idempotent (no-op when already at head), so this is safe to run on every
cold start. Adds ~1 s to cold-start latency, which is well within the
budget for a portfolio API.
"""

from __future__ import annotations

import os
import sys

from mangum import Mangum


def _run_migrations() -> None:
    """Apply pending Alembic migrations against the configured database.

    Imported lazily so unit tests that exercise the handler module don't
    incur the cost of loading Alembic / SQLAlchemy unless the migration
    block actually fires.
    """
    from alembic import command
    from alembic.config import Config

    # ``/var/task`` is the LAMBDA_TASK_ROOT inside the container.
    config = Config("/var/task/alembic.ini")
    config.set_main_option("script_location", "/var/task/alembic")

    # Resolve the (possibly Secrets-Manager-hydrated) DB URL once and pass
    # it to Alembic explicitly so it doesn't have to reach into our pydantic
    # Settings object on its own.
    from app.core.config import get_settings

    settings = get_settings()
    config.set_main_option("sqlalchemy.url", settings.database_url)

    command.upgrade(config, "head")
    print("[lambda_handler] alembic upgrade head completed", file=sys.stderr)


# Only run migrations when actually executing inside Lambda. The
# AWS_LAMBDA_FUNCTION_NAME env var is set automatically by the Lambda
# runtime and is never present in pytest / local dev.
if os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
    _run_migrations()


from app.main import app  # noqa: E402  (intentionally imported after migrations)

# ``lifespan="off"`` skips FastAPI's startup / shutdown events. Those don't
# map cleanly to Lambda's per-invocation lifecycle (the container can be
# frozen and thawed between invocations), and our app does not need them.
handler = Mangum(app, lifespan="off")
