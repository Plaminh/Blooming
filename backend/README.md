# Blooming API

FastAPI/Python backend for Blooming. PostgreSQL is connected through async
SQLAlchemy 2.x with Psycopg 3, and Alembic owns schema migrations from the
existing `database/install.sql` baseline forward.

## Run locally

Use the existing repository virtual environment:

```cmd
cd E:\Blooming\backend
E:\Blooming\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

- Health: http://127.0.0.1:8000/api/v1/health
- Database health: http://127.0.0.1:8000/api/v1/health/db
- Interactive API documentation: http://127.0.0.1:8000/docs

On Windows, psycopg's async driver requires a selector event loop. `--reload`
provides one. Without `--reload`, pass the loop factory explicitly:

```cmd
E:\Blooming\.venv\Scripts\python.exe -m uvicorn app.main:app --loop app.core.runtime:selector_loop_factory
```

## Structure and scope

`app/main.py` creates the application and includes `app/api/main.py`'s
aggregate router. Route modules live in `app/api/routes/`; configuration and
security live in `app/core/`. `app/api/deps.py` holds shared dependencies.

Only health is implemented. Auth, users, assistant, planning, focus, goals,
and garden declare empty routers. Authentication, AI, scheduling, and other
business features remain future work.

## Database

| Path | Purpose |
| --- | --- |
| `app/db/base.py` | Declarative `Base` |
| `app/db/session.py` | Async engine and `AsyncSessionLocal` factory |
| `app/db/models/` | The 19 mapped tables, split by baseline scope |
| `app/api/deps.py` | `SessionDep` request-scoped session dependency |
| `app/core/runtime.py` | Selector event loop helpers for psycopg |
| `alembic/` | Migration environment and versions |

Models are async-only; there is no synchronous session path. `SessionDep`
yields one `AsyncSession` per request, rolls back on failure, and always
closes. `Base.metadata.create_all()` is never called: PostgreSQL and Alembic
own the schema.

Model files mirror the `database/migrations/` scopes: `users`, `goals`,
`planning`, `tasks`, `daily_plans`, `focus`, `reminders`, and `garden`.
`heart_events.metadata` is mapped as the `event_metadata` attribute because
`metadata` is reserved on the declarative base.

### Configuration

Settings load through pydantic-settings from the repository `.env`, resolved
from the package location so the working directory does not matter.
Application settings: `PROJECT_NAME`, `API_V1_PREFIX`, `ENVIRONMENT`.
Database settings reuse the Compose variables: `POSTGRES_DB`, `POSTGRES_USER`,
`POSTGRES_PASSWORD`, `POSTGRES_PORT`, plus optional `POSTGRES_HOST`
(default `127.0.0.1`), `DB_ECHO`, `DB_POOL_SIZE`, `DB_MAX_OVERFLOW`, and
`DB_CONNECT_TIMEOUT`.

Credentials are never hard-coded. The password is a `SecretStr` and the URL is
a SQLAlchemy `URL`, so logs and tracebacks render it as `***`.

### Migrations

The 19 tables already exist, so revision `6ebc3e7e2e0e` is an intentionally
empty baseline and the database is stamped to it rather than upgraded into it.

```cmd
cd E:\Blooming\backend
E:\Blooming\.venv\Scripts\alembic.exe current
E:\Blooming\.venv\Scripts\alembic.exe check
```

`alembic.ini` leaves `sqlalchemy.url` empty; `alembic/env.py` builds the URL
from settings and targets `app.db.Base.metadata`. The legacy Spring Boot table
`flyway_schema_history` is excluded from autogenerate comparison and is never
mapped or dropped. Alembic's own `alembic_version` table is retained.

## Verification

From the repository root:

```cmd
E:\Blooming\.venv\Scripts\python.exe -m pip install -r backend\requirements.txt
E:\Blooming\.venv\Scripts\python.exe -m compileall backend\app backend\alembic
```

From `backend`:

```cmd
E:\Blooming\.venv\Scripts\alembic.exe check
```

`requirements.txt` records direct dependency versions observed in the existing
`E:\Blooming\.venv`. No environment recreation or package upgrade is needed.

## References

- [Bigger Applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
- [Official Full Stack FastAPI Template](https://github.com/fastapi/full-stack-fastapi-template/tree/master/backend/app)
- [SQLAlchemy asyncio](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Alembic](https://alembic.sqlalchemy.org/en/latest/)
