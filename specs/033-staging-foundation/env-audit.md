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

*Note: No dead keys were found that can be safely removed at this time.*
