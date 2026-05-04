# Expense Tracker API

REST API para llevar control de gastos personales: usuarios, categorías, gastos y reportes agregados.

Construido con **FastAPI**, **SQLAlchemy 2**, **PostgreSQL**, **Alembic**, **JWT** y **Pytest**. Empaquetado con Docker y desplegado vía GitHub Actions.

> Status: 🚧 en desarrollo activo.

---

## Stack

- **API**: FastAPI + Pydantic 2
- **DB**: PostgreSQL 16 (vía Docker en local)
- **ORM**: SQLAlchemy 2 (sintaxis moderna con `Mapped[]`)
- **Migraciones**: Alembic
- **Auth**: JWT (HS256) — implementación propia, sin proveedores externos
- **Tests**: Pytest + httpx + cobertura ≥ 70%
- **CI/CD**: GitHub Actions
- **Deploy**: Render

## Quickstart (local)

```bash
# 1. Clonar + entrar
git clone https://github.com/KevinMM007/expense-tracker-api.git
cd expense-tracker-api

# 2. Crear venv e instalar deps
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/Mac
pip install -r requirements-dev.txt

# 3. Levantar Postgres
docker compose up -d

# 4. Variables de entorno
copy .env.example .env          # Windows
# cp .env.example .env          # Linux/Mac

# 5. Migrar base de datos
alembic upgrade head

# 6. Correr la API
uvicorn app.main:app --reload

# Docs interactivas:
# http://localhost:8000/docs
```

## Tests

```bash
pytest --cov=app --cov-report=term-missing
```

## Estructura

```
app/
├── api/v1/           # Routers versionados
├── core/             # Config, DB, security
├── crud/             # Operaciones de base de datos
├── models/           # Modelos SQLAlchemy
└── schemas/          # Schemas Pydantic
tests/                # Suite de tests
alembic/              # Migraciones (generadas)
```

## Roadmap

- [x] Scaffold + Postgres en Docker
- [ ] Modelos: User, Category, Expense
- [ ] Auth con JWT (register / login / me)
- [ ] CRUD de categorías y gastos
- [ ] Endpoint de reportes (gastos por mes / categoría)
- [ ] Tests con cobertura ≥ 70%
- [ ] Dockerfile productivo + GitHub Actions
- [ ] Deploy en Render

---

Hecho por [Kevin Morales](https://github.com/KevinMM007).
