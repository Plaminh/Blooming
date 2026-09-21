# Blooming API

FastAPI/Python backend for Blooming. PostgreSQL is connected through async
SQLAlchemy 2.x with Psycopg 3. `database/install.sql` is the authoritative fresh
installer. The schema is fully maintained in SQL files (one table per file).

## Run locally

Start PostgreSQL from the repository root with the backend environment file:

```cmd
docker compose --env-file backend/.env up -d postgres
```

Compose does not automatically read `backend/.env`. If an existing PostgreSQL
volume was initialized with another password, update that volume's database
user password to match `POSTGRES_PASSWORD` in `backend/.env`; recreating the
container alone does not change passwords stored in an existing volume.

Use the repository scripts to start the backend. This automatically sets `PYTHONPYCACHEPREFIX` to store bytecode in `.cache/python` instead of creating `__pycache__` directories throughout the source.

From the repository root:

```cmd
npm run backend
```

- Health: http://127.0.0.1:8000/api/v1/health
- Database health: http://127.0.0.1:8000/api/v1/health/db
- Interactive API documentation: http://127.0.0.1:8000/docs

On Windows, psycopg's async driver requires a selector event loop. `--reload`
provides one. Without `--reload`, pass the loop factory explicitly:

```cmd
npm run python -- -m uvicorn app.main:app --loop app.core.runtime:selector_loop_factory
```

## Structure and scope

`app/main.py` creates the application and includes `app/api/main.py`'s
aggregate router. Route modules live in `app/api/routes/`; configuration and
security live in `app/core/`. `app/api/deps.py` holds shared dependencies.

Health, auth, users/settings, assistant, planning, focus, goals, garden,
reminders, Today and statistics routes are registered. Goals and Reminders use
the shared SessionDep/CurrentUser dependencies, including request rollback.

## Database

| Path | Purpose |
| --- | --- |
| `app/db/base.py` | Declarative `Base` |
| `app/db/session.py` | Async engine and `AsyncSessionLocal` factory |
| `app/db/models/` | The 23 mapped tables |
| `app/api/deps.py` | `SessionDep` request-scoped session dependency |
| `app/core/runtime.py` | Selector event loop helpers for psycopg |

Models are async-only; there is no synchronous session path. `SessionDep`
yields one `AsyncSession` per request, rolls back on failure, and always
closes. `Base.metadata.create_all()` is never called: The authoritative schema lives under `database/tables/`.

`reward_events.metadata` is mapped as the `event_metadata` attribute because
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

## Verification

From the repository root:

```cmd
npm run python -- -m pip install -r backend\requirements.txt
npm run python -- -m compileall backend\app
npm run test:backend
```

`requirements.txt` records direct dependency versions observed in the existing
`E:\Blooming\.venv`. No environment recreation or package upgrade is needed.

## References

- [Bigger Applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
- [Official Full Stack FastAPI Template](https://github.com/fastapi/full-stack-fastapi-template/tree/master/backend/app)
- [SQLAlchemy asyncio](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
