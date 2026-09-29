# Implementation Plan: Block 0 - Staging Architecture Decisions

## 1. Repository Inspection
Inspect current implementation before proposing changes:
- Checked `backend/app/core/config.py` for `ACCESS_TOKEN_EXPIRE_MINUTES`.
- Checked `backend/app/core/config.py` for Brevo usage and `EMAIL_VERIFICATION_FRONTEND_URL`.
- Checked `docs/architecture/` (did not exist).

## 2. Reflected Decisions
- **ADR-001 (Session Lifetime)**: Created `docs/architecture/ADR-001-staging-session-lifetime.md`. Updated `.env.example` to document `1440` for staging.
- **ADR-002 (Email Verification)**: Created `docs/architecture/ADR-002-hosted-email-verification.md`. Documented the `EMAIL_VERIFICATION_FRONTEND_URL` contract in `.env.example`.
- **ADR-003 (Reminder Ownership)**: Created `docs/architecture/ADR-003-reminder-timing-ownership.md`. Defined the Svelte `resync()` contract and Rust trigger responsibilities.

## 3. Minimal Configuration Changes
- `ACCESS_TOKEN_EXPIRE_MINUTES` is documented in `.env.example`.
- `EMAIL_VERIFICATION_FRONTEND_URL` is documented in `.env.example`.

## 4. Deferred Work
- Block 0.5: minimal `.env.staging` + `tauri.staging.conf.json`.
- Block 4/5: Reminder polling refactor, sleep/resume implementation.
- Post-MVP / Future: Tauri deep links.
- Block 6: CSP.
- Production Hardening: Refresh tokens.

## 5. Validation
- No localhost assumption remains in the documented staging verification contract.
- 24h staging token policy is explicit in ADR and `.env.example`.
- Reminder ownership has exactly one clear boundary documented.
- No accidental refresh-token/deep-link/reconnect implementation is introduced.

## 6. File-by-file Change Plan
1. **`docs/architecture/ADR-001-staging-session-lifetime.md`**: Create ADR for 24h staging token and deferred refresh tokens.
2. **`docs/architecture/ADR-002-hosted-email-verification.md`**: Create ADR for hosted route vs Brevo.
3. **`docs/architecture/ADR-003-reminder-timing-ownership.md`**: Create ADR for Rust trigger and Svelte `resync()`.
4. **`docs/architecture/README.md`**: Create index to include new ADRs.
5. **`.env.example`**: Ensure `ACCESS_TOKEN_EXPIRE_MINUTES` and `EMAIL_VERIFICATION_FRONTEND_URL` are present with comments for staging.
