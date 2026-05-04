#!/usr/bin/env bash
set -euo pipefail

# Apply pending migrations on startup. Idempotent — safe to run every boot.
echo "[entrypoint] Running database migrations..."
alembic upgrade head

echo "[entrypoint] Starting Uvicorn on 0.0.0.0:${PORT:-8000}"
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
