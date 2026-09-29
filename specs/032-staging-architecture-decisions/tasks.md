# Implementation Tasks: Block 0 - Staging Architecture Decisions

## Phase 1 - Repository audit
- [x] locate auth token lifetime configuration
- [x] locate auth error handling
- [x] locate Brevo email verification URL generation
- [x] locate frontend verification route
- [x] locate reminder polling
- [x] locate Tauri timing/lifecycle ownership
- [x] locate existing architecture documentation (did not exist, created directory)

## Phase 2 - ADR-001 Session Lifetime
- [x] document current 30-minute behavior
- [x] document staging decision: 1440 minutes
- [x] document distinction between network failures and real 401 auth failures
- [x] document refresh-token work as deferred
- [x] update configuration documentation/example only if necessary (`.env.example`)

## Phase 3 - ADR-002 Email Verification
- [x] document Brevo as email delivery provider
- [x] document hosted staging `/verify-email` route
- [x] document localhost as development-only
- [x] document deep linking as deferred
- [x] identify configuration contract for `EMAIL_VERIFICATION_FRONTEND_URL` (`.env.example`)

## Phase 4 - ADR-003 Reminder Ownership
- [x] document Rust/Tauri as timing/lifecycle trigger owner
- [x] document Svelte as synchronization/data-fetch owner
- [x] define the future centralized `resync()` contract
- [x] document allowed resync triggers
- [x] document that actual implementation belongs to later blocks

## Phase 5 - Consistency check
- [x] make sure architecture docs and current project docs do not contradict the three decisions
- [x] ensure no later-block functionality was accidentally implemented
- [x] record deferred items clearly

## Phase 6 - Validation
- [x] verify all three ADRs have: context, decision, rationale, consequences/boundaries, deferred work
- [x] verify Block 0 Definition of Done
