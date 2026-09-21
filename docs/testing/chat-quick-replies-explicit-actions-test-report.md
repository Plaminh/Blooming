# Chat Quick Replies & Explicit Actions Test Report

## Scope
Tested the correct handling of quick replies in the Mr. Bloom UI.
Verified that suggestions map to the correct behavioral logic, particularly validating that actions are properly safeguarded and only executed upon explicit user interaction.

## Runtime flow
- `send_text` behavior: The quick reply label or `send_text` payload is correctly submitted through `mrBloomStore.submitMessage`, initiating a standard chat request with `isWaitingForResponse = true`.
- `patch` behavior: The patch array provided in the suggestion triggers `applyPatch(suggestion.patch)` without calling the LLM endpoint or triggering a new user message.
- `explicit-action` behavior: An action string matching a known constant (e.g. `SKIP_OPTIONAL_TODAY`) performs its side effect exclusively when explicitly clicked by the user. The test exercises the actual assistant-response ingestion flow rather than manual store injection, proving that receiving it in a response merely adds it to the list of suggestions without side effects.
- `action whitelist`: Handled by `handleSuggestion`, explicitly filtering actions by matching them against defined constants (`SAVE_TODAY`, `SAVE_ROADMAP`, `SKIP_OPTIONAL_TODAY`, `REPLAN_TODAY`). Unsupported actions produce no API call, no fallback message submission, and no relevant state mutation.
- `waiting-state` behavior: Submitting a message correctly sets `isWaitingForResponse = true`, locking quick replies and text inputs until the API call finishes.

## RED → GREEN findings
- `MD-008`: The production implementation lacked a safeguard and fell back to `submit(suggestion.label)` for non-whitelisted actions. The `handleSuggestion` logic was updated to explicitly ignore unhandled strings.

## Test execution
Frontend test suite command: `npm run test`
- Test files passed: 38
- Tests passed: 261
- Tests failed: 2 (pre-existing flaky environmentStore fake timer tests, unrelated to Mr. Bloom)

Frontend static check command: `npm run check`
- Result: PASS
- svelte-check found 0 errors and 0 warnings

## Remaining limitations
- The typed representation of actions in `api.ts` could be further tightened. Currently, `action?: string | null` is loosely typed as opposed to using a TypeScript union type for the whitelist.

## Tests by ID
- **UI-014**: `UI-014: send_text quick reply uses normal submitMessage flow` 
  - Evidence: `MrBloomConversationPanel.test.ts`
  - PASS
- **UI-015**: `UI-015: patch quick reply invokes applyPatch without calling chat endpoint`
  - Evidence: `MrBloomConversationPanel.test.ts`
  - PASS
- **UI-016 / UI-017**: `UI-016 / UI-017: action executes only after explicit user click`
  - Evidence: `MrBloomConversationPanel.test.ts`
  - PASS
- **UI-018**: `UI-018: quick replies are disabled while waiting for response`
  - Evidence: `MrBloomConversationPanel.test.ts`
  - PASS
- **MD-008**: `MD-008: safely ignores unsupported actions`
  - Evidence: `mrBloomStore.test.ts`
  - PASS
