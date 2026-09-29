# Environment Variable Audit (Block 1)

| Key | Consumer | Environment | Status | Action |
|---|---|---|---|---|
| `PUBLIC_API_BASE_URL` | Frontend API Client | All | ACTIVE | KEEP |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Backend Auth | All | ACTIVE | KEEP (Dev 30, Staging 1440) |
| `EMAIL_VERIFICATION_FRONTEND_URL` | Backend Auth | All | ACTIVE | KEEP (Hosted in staging) |
| `FRONTEND_URLS` | Backend CORS | All | ACTIVE | KEEP |
| `BREVO_API_KEY` | Backend Email | Prod/Staging | ACTIVE | KEEP |
| `BREVO_SENDER_EMAIL` | Backend Email | Prod/Staging | ACTIVE | KEEP |
| `BREVO_SENDER_NAME` | Backend Email | Prod/Staging | ACTIVE | KEEP |
| `SECRET_KEY` | Backend Core | All | ACTIVE | KEEP |
| `POSTGRES_DB` | Backend DB | All | ACTIVE | KEEP |
| `POSTGRES_USER` | Backend DB | All | ACTIVE | KEEP |
| `POSTGRES_PASSWORD` | Backend DB | All | ACTIVE | KEEP |
| `POSTGRES_HOST` | Backend DB | All | ACTIVE | KEEP |
| `POSTGRES_PORT` | Backend DB | All | ACTIVE | KEEP |
| `GROQ_API_KEY` | Backend AI | All | ACTIVE | KEEP |
| `GROQ_BASE_URL` | Backend AI | All | ACTIVE | KEEP |
| `OLLAMA_BASE_URL` | Backend AI | Dev | ACTIVE | KEEP |
| `ENVIRONMENT` | Backend config validation | All | ACTIVE / STAGING_REQUIRED | KEEP, DOCUMENT |
| `LOG_LEVEL` | Backend JSON logging | All | ACTIVE | KEEP |
| `GIT_SHA` | Readiness/build identity | Staging/Prod | STAGING_REQUIRED | KEEP |
| `LATEST_SCHEMA_MIGRATION` | Readiness migration gate | All | ACTIVE | KEEP |
| `DB_ECHO` | SQLAlchemy diagnostics | Development | DEVELOPMENT_ONLY | KEEP |
| `DB_POOL_SIZE` | SQLAlchemy engine | Staging/Prod | ACTIVE | KEEP |
| `DB_MAX_OVERFLOW` | SQLAlchemy engine | Staging/Prod | ACTIVE | KEEP |
| `DB_CONNECT_TIMEOUT` | SQLAlchemy engine | All | ACTIVE | KEEP |
| `AI_ROUTE_*` | LLM route configuration | All | ACTIVE | KEEP |
| `AI_*BUDGET*`, `AI_*RATE_LIMIT*`, `AI_TIMEOUT_SECONDS` | AI safeguards | All | ACTIVE | KEEP |
| `BACKEND_PORT` | Compose host binding | Local rehearsal | DEVELOPMENT_ONLY | KEEP |
| `MIGRATION_DATABASE_URL` | Release job | Staging/Prod | STAGING_REQUIRED | DOCUMENT; never expose to app/frontend |

No keys were proven dead by repository search. No uncertain key was removed. Frontend receives only `PUBLIC_API_BASE_URL`; all credentials remain backend/release-job only.
