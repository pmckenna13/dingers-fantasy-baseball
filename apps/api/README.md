# apps/api — FastAPI backend

Async FastAPI service: SQLAlchemy 2.0 (async), Alembic migrations, Pydantic
v2 schemas, JWT auth (see [ADR-0001](../../docs/adr/0001-jwt-over-sessions.md)).

## Run locally without Docker

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
cp .env.example .env   # then point DATABASE_URL/REDIS_URL at local services

alembic upgrade head
uvicorn app.main:app --reload
```

Docs: http://localhost:8000/docs · Health: http://localhost:8000/api/v1/health

## Tests

```bash
pytest -v --cov=app
```

Tests run against an in-memory SQLite DB and a fake in-memory Redis stand-in
(see `tests/conftest.py`) — no external services required to run the suite.

## Migrations

```bash
alembic revision --autogenerate -m "describe the change"
alembic upgrade head
```
