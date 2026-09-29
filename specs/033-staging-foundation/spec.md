# Feature Specification: Block 1 - Staging Foundation & Runtime Blockers

**Feature Branch**: `feature/staging-readiness`
**Status**: Active

## Goal
Create the minimum staging foundation required to test Blooming as a real packaged Tauri desktop application.

## User Scenarios
- **Scenario 1 - Packaged staging launch**: Packaged staging application starts without frontend dev server. (NOT VERIFIED)
- **Scenario 2 - Backend connection**: Reaches configured backend API. (NOT VERIFIED)
- **Scenario 3 - Double launch**: Second launch does not create another instance. (NOT VERIFIED)
- **Scenario 4 - Development compatibility**: Normal development workflow still works. (PASS - test timeouts are unrelated pre-existing baseline issues)
- **Scenario 5 - Verification configuration**: Verification uses hosted URL, not localhost. (PASS)

## Functional Requirements
- Staging API URL must be environment-driven.
- Development config must continue to work.
- Backend CORS must support packaged Tauri origins (`http://tauri.localhost`, `tauri://localhost`).
- Staging auth token lifetime = 1440 minutes.
- Staging verification URL must use hosted route.
- Single-instance protection enabled.

## Architecture & Configuration Requirements
- `ACCESS_TOKEN_EXPIRE_MINUTES=1440` in staging.
- `EMAIL_VERIFICATION_FRONTEND_URL=https://<staging-frontend>/verify-email`
- `tauri.staging.conf.json` created.
- `.env.staging` for frontend environment variables.

## Edge Cases
- Network failures are distinct from authentication failures (Deferred to Reliability block).
- Unknown env variables are documented, not deleted.

## Out of Scope
- Refresh tokens.
- Deep links.
- Full CSP hardening.
- Widget behavior/autostart changes.
- Rust logging, resync, reconnect.
- DB migrations.

## Success Criteria
- [x] Staging-specific packaged Tauri build config. (PASS)
- [x] Backend CORS supports packaged Tauri origins. (PASS)
- [x] Existing development workflow still works. (PASS - test timeouts are unrelated pre-existing issues)
- [ ] Second launch does not create a second instance. (NOT VERIFIED)
- [x] Staging access token configured to 1440 mins. (PASS)
- [x] Verification config uses hosted URL. (PASS)
- [x] Repo ignore rules protect secrets. (PASS)
- [x] Env variable audit complete. (PASS)
