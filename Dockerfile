# syntax=docker/dockerfile:1.7

# ---------- Builder stage ----------
FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Build deps for psycopg / bcrypt wheels (kept out of the runtime image)
RUN apt-get update \
 && apt-get install -y --no-install-recommends build-essential libpq-dev \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --prefix=/install -r requirements.txt


# ---------- Runtime stage ----------
FROM python:3.13-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000

# Runtime libs only (libpq for psycopg)
RUN apt-get update \
 && apt-get install -y --no-install-recommends libpq5 \
 && rm -rf /var/lib/apt/lists/* \
 && groupadd --system app && useradd --system --gid app --create-home app

WORKDIR /app

# Copy installed Python packages from the builder
COPY --from=builder /install /usr/local

# Copy application code
COPY app ./app
COPY alembic ./alembic
COPY alembic.ini ./alembic.ini
COPY entrypoint.sh ./entrypoint.sh

RUN chmod +x ./entrypoint.sh && chown -R app:app /app

USER app

EXPOSE 8000

# Render (and most PaaS) inject $PORT — entrypoint honors it.
ENTRYPOINT ["./entrypoint.sh"]
