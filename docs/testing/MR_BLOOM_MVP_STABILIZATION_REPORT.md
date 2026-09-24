# Mr. Bloom MVP Stabilization Report

## Scope included

This pass audited and stabilized draft editing, Today preview/save/replace, Goal/Roadmap editing and atomic save, clarification/session restoration, ownership filtering, trusted server history, safe rendering, and provider-boundary behavior. Existing valid scheduler, token, ownership, and persistence work was retained.

## Post-MVP / deferred

Complex circuit-breaker behavior, rolling 24-hour budget refinements, duration calibration, proactive widget nudges, live LLM evaluation, advanced metrics, multi-level degraded operation, Phase J expansion, Phase L, and a true automated browser/API/PostgreSQL Phase M matrix remain **POST-MVP / DEFERRED**. Existing mocked `Block7_E2E`, `Block8_E2E`, and `Block9_E2E` files are not true E2E evidence and are not reported as such.

## Blocking defects found and fixed

- Removed `fix_svelte.mjs`; no other one-off helper scripts remain in the diff.
- Replaced the empty deterministic-editor test with an async production-path test and a spy at the provider boundary.
- Replaced the falsely named `E2E_002_draft_editor.test.ts` with `draftEditorStore.integration.test.ts`; mocks are installed before actions/timers.
- Removed the introduced unsafe `PatchOp` `any` and typed session structured payloads.
- Reworked Today save cleanup so old errors do not block retry, duplicate clicks are rejected, and every return clears pending state.
- Added immediate preview invalidation/local title-duration updates, serialized patches, request revisions, stale preview rejection, and deterministic pending cleanup.
- Preserved the reviewed preview across `PLAN_EXISTS` and Cancel; Confirm sends exactly one replace request without regenerating.
- Added stable per-save-attempt Roadmap keys and user-scoped database uniqueness.
- Added deterministic next-free milestone IDs (`m1..mn`) without renumbering existing milestones.
- Enforced ordered roadmap milestones and server-timezone past-date validation before persistence.
- Bound Today preview tokens to user, canonical draft, and plan revision; stale/cross-user capabilities are rejected.
- Preserved completed/elapsed Today blocks during replace and kept Goal/milestone and Today persistence transactional.
- Removed dead in-memory rate-limiter wiring from the assistant request path; the retained request-path limiter is user-scoped and database-backed.
- Corrected deferred-save API paths and made rollback evidence traverse the API transaction boundary.

## Production files changed (purpose)

- `backend/app/ai/{editor_rules.py,patches.py}` and `handlers/{editor.py,planner.py,roadmap.py}`: deterministic edits, atomic patches, stable IDs, parser preservation, preview integration.
- `backend/app/api/routes/{assistant.py,goals.py}`: trusted history, continuation/restore, ownership, database rate limit, validation error contract.
- `backend/app/services/{today_service.py,goals_service.py,assistant_service.py}`: versioned preview/save, idempotency, replace preservation, atomic Goal save, session completion.
- `backend/app/schemas/{drafts.py,patches.py,goals.py,today.py}`: canonical discriminated contracts and roadmap/save validation.
- `backend/app/db/models/goals.py`, `database/tables/07_goals.sql`, `database/migrations/03_goal_idempotency.sql`: nullable user-scoped Goal idempotency persistence.
- `frontend/src/lib/api.ts`: typed patch/session/save contracts and explicit Roadmap idempotency key.
- `frontend/src/lib/features/mr-bloom/stores/mrBloomStore.ts`: deterministic edit/preview/save state machine and retry-safe persistence.
- Mr. Bloom draft, timeline, roadmap, and replace-dialog components: editable reviewed drafts and explicit save/replace UI.

## Test traceability

| Behavior | Evidence |
|---|---|
| Deterministic edit, zero provider calls; unknown ID; immutability; atomic multi-op; stable IDs | `test_phase_d_editor.py` |
| No persistence before save; Today save/reload/idempotency/stale/cross-user/rollback; Goal atomicity/idempotency/validation; trusted history | `test_phase_e_to_m_acceptance.py`, `test_deferred_save.py`, `test_today_preview.py`, `test_assistant_security.py` |
| Immediate invalidation, debounce, refreshed token, preview failure cleanup | `draftEditorStore.integration.test.ts` |
| Retry, duplicate click, replace Cancel/Confirm, deterministic milestone IDs | `mrBloomStore.test.ts` |
| Safe text rendering | existing Mr. Bloom component tests |

## Exact command evidence

All commands ran from the working directories shown.

| Working directory | Command | Passed | Failed | Skipped | Exit |
|---|---|---:|---:|---:|---:|
| `E:\Blooming\backend` | `..\.venv\Scripts\python.exe -m pytest tests/unit/test_phase_d_editor.py tests/unit/test_assistant_schemas.py tests/api/test_phase_e_to_m_acceptance.py tests/api/test_deferred_save.py tests/api/test_today_preview.py tests/api/test_assistant_security.py -q` | 39 | 0 | 0 | 0 |
| `E:\Blooming\backend` | focused rerun of formerly failing Block 7/8/9, focus, and parser tests | 10 | 0 | 0 | 0 |
| `E:\Blooming\backend` | `..\.venv\Scripts\python.exe -m pytest tests -q` | 522 | 0 | 0 | 0 |
| `E:\Blooming\frontend` | `npm run check` | 1 command | 0 diagnostics | 0 | 0 |
| `E:\Blooming\frontend` | focused store/component Vitest command | 21 | 0 | 0 | 0 |
| `E:\Blooming\frontend` | `npm test -- --run` | 274 | 27 | 0 | 1 |
| `E:\Blooming\backend` | app import smoke check | 1 | 0 | 0 | 0 |

The broad frontend run failed in unrelated timing/canvas suites and legacy mocked files named E2E; the Mr. Bloom subset also has 14 legacy UI-query failures. These are not claimed as passes or as true E2E coverage.

## Database integration result

Ephemeral PostgreSQL 17 integration ran successfully through Testcontainers. The focused 39-test command exercised actual PostgreSQL schemas and transactions, including rollback, idempotency, ownership isolation, session completion, and reload. Bootstrap SQL and migration both define a nullable `source_idempotency_key` with a unique partial index on `(user_id, source_idempotency_key)`.

## Remaining known limitations

- No true browser-to-API-to-PostgreSQL automated E2E harness was run; E2E-002 is deferred to manual acceptance.
- The broad frontend regression suite is not green (27 failures), dominated by unrelated timeouts/canvas limitations and legacy mocked “E2E” query assumptions.
- Advanced/post-MVP items listed above remain intentionally incomplete.

## Manual UI checklist

- Create/edit/add/remove a Today draft, generate a real preview, save, and reload Today.
- Apply an overload repair and verify a new server preview precedes Save.
- Verify existing-plan Cancel preserves draft/preview; Confirm replaces only unfinished future work.
- Create/edit a Roadmap and milestones, save, retry, and reload Goals.
- Reload an open session; verify messages/draft restore and stale preview cannot save.
- Exercise preview/save/provider failures; verify input/draft remain, loading clears, and retry works.
- Enter HTML-like user text and confirm it renders as text.

## Final verdict

**READY FOR MANUAL UI TESTING**, with the broad frontend regression failures and absence of true automated E2E explicitly recorded above. PostgreSQL integration is available and passed for the focused MVP flows.
