# Blooming API

FastAPI/Python skeleton for Blooming. PostgreSQL, SQLAlchemy, psycopg, and
Alembic are the persistence direction; connections, models, and migrations
are not implemented.

## Run locally

Use the existing repository virtual environment:

```cmd
cd E:\Blooming\backend
E:\Blooming\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

- Health: http://127.0.0.1:8000/api/v1/health
- Interactive API documentation: http://127.0.0.1:8000/docs
- Health response: `{"status":"ok","service":"blooming-api"}`

## Structure and scope

`app/main.py` creates the application and includes `app/api/main.py`'s
aggregate router. Route modules live in `app/api/routes/`; configuration and
future database/security integration live in `app/core/`.
`app/api/deps.py` is reserved for shared dependencies.

Only health is implemented. Auth, users, assistant, planning, focus, goals,
and garden declare empty routers. Authentication, AI, scheduling, and other
business features remain future work. `tests/__init__.py` initializes the
test package; no feature tests are claimed.

Settings use pydantic-settings and read environment variables:
`PROJECT_NAME` (default `Blooming API`), `API_V1_PREFIX` (default
`/api/v1`), and `ENVIRONMENT` (default `development`).
The skeleton does not load an .env file or require secrets/database settings.

`requirements.txt` records direct dependency versions observed in the existing
`E:\Blooming\.venv`. No environment recreation or package upgrade is needed.

## Verification

From the repository root:

```cmd
E:\Blooming\.venv\Scripts\python.exe -m compileall backend\app
E:\Blooming\.venv\Scripts\python.exe -c "import sys; sys.path.insert(0, 'backend'); from app.main import app; print(app.title)"
```

## References

- [Bigger Applications](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
- [Official Full Stack FastAPI Template](https://github.com/fastapi/full-stack-fastapi-template/tree/master/backend/app)
