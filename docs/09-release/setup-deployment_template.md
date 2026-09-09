# Setup and Deployment Guide

## Local prerequisites

| Tool | Version | Verification |
|---|---|---|
| `<TOOL>` | `<VERSION>` | `<COMMAND>` |

## Configuration

| Variable | Required | Safe example | Purpose |
|---|---:|---|---|
| `DATABASE_URL` | Yes | `<PLACEHOLDER>` | Database connection |

<!-- Never include actual secrets. Keep placeholders in .env.example. -->

## Run locally

```bash
<COMMANDS>
```

## Database migration and seed

```bash
<COMMANDS>
```

## Health and test checks

| Service/check | Command or URL | Expected |
|---|---|---|
| `<SERVICE>` | `<CHECK>` | `<RESULT>` |

## CI checks

- Frontend: `<LINT_TEST_BUILD>`
- Backend: `<TEST_BUILD>`
- Security/dependency: `<CHECKS>`

## Deployment steps

1. Verify the release artifact and recovery point.
2. `<DEPLOYMENT_STEP>`
3. Run health and critical user-flow checks.

## Monitoring

| Signal | Threshold | Response |
|---|---:|---|
| Error rate | `<THRESHOLD>` | `<ACTION>` |
| API/AI latency | `<THRESHOLD>` | `<ACTION>` |
| LLM cost/usage | `<THRESHOLD>` | `<ACTION>` |

## Backup and rollback

- Backup method/frequency: `<DETAILS>`
- Restore verification: `<DETAILS>`
- Rollback trigger: `<THRESHOLD_OR_FAILURE>`
- Previous known-good version: `<VERSION>`
- Rollback steps: `<SCOPED_STEPS>`

## Troubleshooting

| Symptom | Likely cause | Resolution |
|---|---|---|
| `<SYMPTOM>` | `<CAUSE>` | `<ACTION>` |

