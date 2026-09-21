# Message Failure, Retry, and Concurrency Test Report

## Scope
```text
UI-008
UI-009
UI-010
UI-012
SS-011
PR-016
E2E-010
```

## Failure lifecycle
1. `user message` sent and optimistically added to chat history.
2. `pending` state begins (`isWaitingForResponse = true`).
3. If API rejects/times out (`failed`), `isWaitingForResponse = false` and message `status` becomes `'failed'`.
4. `retry` button clicked by user via `mrBloomStore.retryMessage`.
5. `pending` state begins again, message `status` cleared.
6. On API resolution (`success`), response added and state mutated correctly.

## Retry identity
The implementation maps exactly one failed message + retry = one logical user turn. This is achieved in `submit()` by passing the existing `msgId` via `retryId`, which explicitly prevents appending a new user message to the `chatHistory` array, and instead clears the `status: 'failed'` flag of the existing user message in place.

## Concurrency protection
- **mechanism**: A monotonic `latestRequestVersion` counter scoped to the store.
- **request identity/version**: Captures the counter value exactly when `sendMessage` is invoked. If the captured value does not equal `latestRequestVersion` upon resolution, the response is discarded entirely.
- **which response-owned fields are guarded**: `activeDraft`, `preview`, `previewMode`, `sessionId`, `degraded`, `suggestions`, `assumptions`, `chatHistory`, and `error`. The entire response application is guarded atomically.
- **authoritative transitions**: Public store actions that legitimately make a pending assistant response obsolete (`restoreLatestSession`, `discardDraft`, `acceptDraft`, `saveToday`, `persistRoadmap`) increment `latestRequestVersion`, safely aborting any late-resolving chat request from overwriting the new user-intended context.

## Timeout behavior
- **provider timeout**: Simulated frontend assistant request failure/timeout.
- **backend behavior**: Not independently asserted by this frontend test suite.
- **frontend behavior**: The API client rejects the promise, triggering `catch (error)` in `sendMessage`.
- **user message state**: Remains in `chatHistory` with `status: 'failed'`.
- **retry availability**: The `Gửi lại` button appears inline, allowing the user to replay the turn.

## Test coverage

| ID | Test | Evidence | Result |
|---|---|---|---|
| UI-008 | `UI-008, UI-009...: Message failure and retry lifecycle` | Proves message remains after failure and retry button renders. | PASS |
| UI-009 | `UI-008, UI-009...: Message failure and retry lifecycle` | Proves retry resets pending state and retains exactly 1 user message. | PASS |
| UI-010 | `UI-010: Double-click Send protection` | Proves rapid double-click on `Send` creates exactly 1 API request. | PASS |
| UI-012 | `UI-008, UI-009...: Message failure and retry lifecycle` | Proves the UI properly transitions out of failure state upon retry. | PASS |
| SS-011 | `SS-011, PR-016: Stale response protection` | Proves late resolving request A does not restore a stale `session_id` after `discardDraft`. | PASS |
| PR-016 | `SS-011, PR-016: Stale response protection` | Proves late resolving request A does not restore an `activeDraft` after `discardDraft`. | PASS |
| E2E-010 | `UI-008, UI-009...: Message failure and retry lifecycle` | Proves a simulated timeout/network error securely invokes the failure lifecycle. | PASS |

## RED -> GREEN
No genuine production defects were found for Block 5 UI flows (`UI-008`-`UI-010`, `UI-012`, `E2E-010`); existing failure state and in-flight guards successfully protected them. 

**Test: `SS-011`, `PR-016` (Stale responses)**
- **Initial failure**: A pending chat request (`Request A`), if it resolved late, would blindly overwrite the active context even if the user had already executed an authoritative action (like `discardDraft` or `restoreLatestSession`) to explicitly change or reset their context.
- **Root cause**: No concurrency protection mechanism inside `sendMessage` to respect subsequent authoritative context transitions.
- **Minimal fix**: Added a `latestRequestVersion` counter, atomically aborting the `update()` call if `version !== latestRequestVersion`. Context-changing actions like `discardDraft` increment the version.
- **Final result**: Safely aborts late-resolving stale responses, preventing them from resurrecting a discarded draft or stale session.
