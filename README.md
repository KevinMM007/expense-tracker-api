# Expense Tracker API

[![CI](https://github.com/KevinMM007/expense-tracker-api/actions/workflows/ci.yml/badge.svg)](https://github.com/KevinMM007/expense-tracker-api/actions/workflows/ci.yml)
[![Python](https://img.shields.io/badge/python-3.13-3776AB.svg?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1.svg?logo=postgresql&logoColor=white)](https://www.postgresql.org/)
[![Coverage](https://img.shields.io/badge/coverage-95%25-brightgreen.svg)](#tests)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> **Production-ready REST API** for personal expense tracking, built end-to-end with a modern Python stack: users, categories, expenses, JWT auth, and aggregated reports — fully containerised, tested, CI-checked and deployed.

---

## 🌐 Live demo

**API** → <https://expense-tracker-api-veer.onrender.com>
**Interactive docs (Swagger UI)** → <https://expense-tracker-api-veer.onrender.com/docs>
**Health check** → <https://expense-tracker-api-veer.onrender.com/api/v1/ping>

> Hosted on Render's free tier — the first request after ~15 minutes of inactivity may take 30-50 s while the instance wakes up.

### Try it in 30 seconds

```bash
BASE="https://expense-tracker-api-veer.onrender.com"

# 1. Register
curl -X POST "$BASE/api/v1/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"email":"demo@example.com","password":"password123","full_name":"Demo"}'

# 2. Login → grab the token
TOKEN=$(curl -s -X POST "$BASE/api/v1/auth/login" \
        -d "username=demo@example.com&password=password123" \
        | python -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

# 3. Create a category and an expense
CAT=$(curl -s -X POST "$BASE/api/v1/categories" \
      -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
      -d '{"name":"Food"}' | python -c "import sys,json;print(json.load(sys.stdin)['id'])")

curl -X POST "$BASE/api/v1/expenses" \
     -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
     -d "{\"amount\":\"42.50\",\"description\":\"Tacos\",\"spent_on\":\"2026-05-04\",\"category_id\":$CAT}"

# 4. Aggregated report
curl "$BASE/api/v1/reports/by-category" -H "Authorization: Bearer $TOKEN"
```

---

## ✨ Features

- 🔐 **JWT authentication** — register, login (OAuth2 password flow) and `/me`, all hand-rolled (no Firebase, no Auth0)
- 👤 **User-scoped data** — every category and expense is filtered by the authenticated user; cross-user reads return 404
- 🗂 **Categories CRUD** — unique name per user enforced both at the API layer (409) and in the schema (`UNIQUE` constraint)
- 💸 **Expenses CRUD** with optional filters: `category_id`, `date_from`, `date_to`, pagination (`skip` / `limit`)
- 📊 **Aggregated reports**: total spent, totals grouped by category, totals grouped by month
- 📦 **Alembic migrations** — auto-generated, applied automatically at container start-up
- 🧪 **27 tests, 95% line coverage** — auth, CRUD, reports, edge cases (cross-user 404, duplicate 409, validation 422)
- 🐳 **Multi-stage Dockerfile** — slim runtime image (~150 MB), runs as a non-root user
- 🤖 **GitHub Actions CI** — lint (`ruff`) → migrations against a real Postgres service → pytest with `--cov-fail-under=70` → docker build with cache
- ☁️ **One-click deploy on Render** — auto-rewrites Heroku/Render-style `postgresql://` URLs for psycopg 3

---

## 🧱 Stack

| Layer | Technology |
|---|---|
| Web framework | **FastAPI 0.115** + Pydantic v2 |
| ORM | **SQLAlchemy 2** (modern `Mapped[]` syntax) |
| Database | **PostgreSQL 16** |
| Migrations | **Alembic** |
| Auth | **JWT (HS256)** + bcrypt password hashing |
| Tests | **Pytest** + httpx + pytest-cov |
| Lint | **Ruff** |
| Container | **Docker** (multi-stage, Python 3.13-slim) |
| CI | **GitHub Actions** |
| Deploy | **Render** (Docker web service + managed Postgres) |

---

## 📚 API overview

| Method | Path | Auth | Description |
|---|---|---|---|
| `GET` | `/` | — | Service info |
| `GET` | `/api/v1/ping` | — | Health check |
| `POST` | `/api/v1/auth/register` | — | Create a user account |
| `POST` | `/api/v1/auth/login` | — | OAuth2 password flow → JWT |
| `GET` | `/api/v1/auth/me` | ✅ | Current authenticated user |
| `GET` | `/api/v1/categories` | ✅ | List your categories |
| `POST` | `/api/v1/categories` | ✅ | Create a category |
| `GET` | `/api/v1/categories/{id}` | ✅ | Read one |
| `PATCH` | `/api/v1/categories/{id}` | ✅ | Rename |
| `DELETE` | `/api/v1/categories/{id}` | ✅ | Delete (cascades to expenses) |
| `GET` | `/api/v1/expenses` | ✅ | List with filters: `category_id`, `date_from`, `date_to`, `skip`, `limit` |
| `POST` | `/api/v1/expenses` | ✅ | Create an expense |
| `GET` | `/api/v1/expenses/{id}` | ✅ | Read one |
| `PATCH` | `/api/v1/expenses/{id}` | ✅ | Update |
| `DELETE` | `/api/v1/expenses/{id}` | ✅ | Delete |
| `GET` | `/api/v1/reports/total` | ✅ | Total spend (optional `date_from`/`date_to`) |
| `GET` | `/api/v1/reports/by-category` | ✅ | Totals grouped by category |
| `GET` | `/api/v1/reports/by-month` | ✅ | Totals grouped by year/month |

Full schemas, request/response examples and an interactive playground live in the auto-generated **Swagger UI** at [`/docs`](https://expense-tracker-api-veer.onrender.com/docs).

---

## 🚀 Quickstart (local)

**Requirements:** Python 3.13, Docker Desktop.

```bash
# 1. Clone
git clone https://github.com/KevinMM007/expense-tracker-api.git
cd expense-tracker-api

# 2. Virtual env + dev deps
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux / Mac
pip install -r requirements-dev.txt

# 3. Spin up PostgreSQL (host port 5433 to avoid colliding with a native install on 5432)
docker compose up -d

# 4. Environment
copy .env.example .env          # Windows
# cp .env.example .env          # Linux / Mac

# 5. Apply migrations
alembic upgrade head

# 6. Run the API with hot-reload
uvicorn app.main:app --reload
```

Open <http://localhost:8000/docs> to play with the API.

---

## 🧪 Tests

```bash
pytest --cov=app --cov-report=term-missing
```

Tests use an **in-memory SQLite database** (`StaticPool`) so the suite runs in a few seconds with zero external dependencies — the CI also re-runs Alembic against a real PostgreSQL service to verify migrations stay in sync with the models.

```
27 passed in 8.07s
TOTAL coverage: 95%
```

---

## 🐳 Run with Docker

```bash
docker compose up -d              # Postgres
docker build -t expense-tracker-api .
docker run --rm -p 8000:8000 \
    -e DATABASE_URL="postgresql+psycopg://expense:expense@host.docker.internal:5433/expense_tracker" \
    -e JWT_SECRET_KEY="change-me" \
    expense-tracker-api
```

The image's entrypoint runs `alembic upgrade head` before starting Uvicorn, so migrations are applied automatically on every boot — perfect for PaaS deploys.

---

## 🔄 CI / CD

Every push and pull request to `main` runs [`.github/workflows/ci.yml`](.github/workflows/ci.yml):

1. **Lint** — `ruff check .`
2. **Migrations** — `alembic upgrade head` against a real Postgres 16 service container
3. **Tests** — `pytest --cov=app --cov-fail-under=70`
4. **Docker build** — multi-stage build with GitHub Actions cache (no push)

Render auto-deploys `main` after CI is green.

---

## 🗂 Project structure

```
expense-tracker-api/
├── alembic/                 # Migration scripts
│   └── versions/
├── app/
│   ├── api/
│   │   ├── deps.py          # FastAPI dependencies (DB session, current_user)
│   │   └── v1/              # Versioned routers (auth, categories, expenses, reports)
│   ├── core/
│   │   ├── config.py        # Pydantic Settings (auto-coerces postgres:// URLs)
│   │   ├── database.py      # SQLAlchemy engine + session factory
│   │   └── security.py      # bcrypt + JWT helpers
│   ├── crud/                # Thin SQLAlchemy query helpers
│   ├── models/              # SQLAlchemy ORM models
│   ├── schemas/             # Pydantic DTOs
│   └── main.py              # FastAPI app factory
├── tests/                   # Pytest suite (auth, CRUD, reports, health)
├── .github/workflows/ci.yml
├── Dockerfile               # Multi-stage, non-root, slim runtime
├── docker-compose.yml       # Local Postgres 16
├── entrypoint.sh            # Migrate → uvicorn
├── alembic.ini
├── pyproject.toml           # Ruff + pytest + coverage config
└── requirements*.txt
```

---

## 📜 License

[MIT](LICENSE)

---

Built by **[Kevin Morales](https://github.com/KevinMM007)** as part of his backend portfolio.
Open to remote junior backend roles in LATAM / USA — let's connect.
