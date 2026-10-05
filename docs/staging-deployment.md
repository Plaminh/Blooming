# Staging deployment runbook

## Required secret configuration

Set `ENVIRONMENT=staging`, `ACCESS_TOKEN_EXPIRE_MINUTES=1440`, `SECRET_KEY`, PostgreSQL application credentials, Brevo credentials, AI provider credentials, `FRONTEND_URLS`, `EMAIL_VERIFICATION_FRONTEND_URL`, and `GIT_SHA` in the platform secret store. Never expose these values to the frontend; only `PUBLIC_API_BASE_URL` is public.

## Database roles

Before every upgrade, create a backup:

```sh
pg_dump --format=custom "$DATABASE_OWNER_URL" --file=blooming-before-upgrade.dump
```

Create a separate login role for the application and grant only runtime rights:

```sql
CREATE ROLE blooming_app LOGIN PASSWORD '<secret>';
GRANT CONNECT ON DATABASE blooming TO blooming_app;
GRANT USAGE ON SCHEMA public TO blooming_app;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO blooming_app;
ALTER DEFAULT PRIVILEGES FOR ROLE blooming_owner IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO blooming_app;
```

Do not grant `CREATE` on the schema or ownership of tables to `blooming_app`. The database owner must ensure `pgcrypto` is available.

Restore verification uses a disposable database and is mandatory before calling the backup usable:

```sh
createdb blooming_restore_check
pg_restore --exit-on-error --dbname=blooming_restore_check blooming-before-upgrade.dump
psql blooming_restore_check -v ON_ERROR_STOP=1 -f database/tests/00_schema_smoke_test.sql
dropdb blooming_restore_check
```

## Release sequence

1. Build and push the backend image tagged with `GIT_SHA`.
2. Deploy one backend worker using the app-role URL.
3. Gate traffic on `GET /api/v1/health/ready`; use `/api/v1/health` for liveness.
4. In `frontend/`, set `PUBLIC_API_BASE_URL` in `.env.staging` to the HTTPS backend URL ending in exactly `/api/v1`, and set the staging CSP `connect-src` in `src-tauri/tauri.staging.conf.json` to that URL's origin. Then run `npm run tauri build -- --config src-tauri/tauri.staging.conf.json`. The staging config runs `npm run build:staging`, which checks the `/api/v1` contract and that the CSP allows the backend origin, then builds with `--mode staging`. A plain `npm run build` ignores `.env.staging`.
5. Verify registration, hosted verification, login, and assistant chat from the installed app.

## CORS

The API always allows the packaged desktop app's own webview origins: `http://tauri.localhost` (Windows), `tauri://localhost` (macOS/Linux) and `https://tauri.localhost`. `FRONTEND_URLS` only needs the web origins, such as the hosted verification page and the dev server. It accepts a JSON list or a comma-separated string. Before this was built in, an installed app whose origin was missing from `FRONTEND_URLS` failed every request, starting with registration, as a generic "Network error".

## CSP status

The checked-in staging CSP is intentionally limited to local packaged testing and allows `connect-src http://127.0.0.1:8000`. It is not the final hosted staging CSP. Before producing a hosted staging installer, replace that entry with the one exact HTTPS API origin and rebuild; do not add wildcard origins.

Unsigned Windows staging installers may trigger SmartScreen. This is expected until production signing is configured.
