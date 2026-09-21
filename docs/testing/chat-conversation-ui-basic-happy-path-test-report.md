# Conversation UI Basic Happy Path Test Report

## Scope
```text
UI-001
UI-002
UI-003
UI-004
UI-005
UI-006
UI-007
UI-011
UI-013
UI-020
```

## Component Map

| Responsibility | Actual implementation |
|---|---|
| Conversation screen | `src/lib/features/mr-bloom/components/organisms/MrBloomConversationPanel.svelte` |
| Composer/input | `src/lib/features/mr-bloom/components/molecules/ChatComposer.svelte` |
| Send handler | `src/lib/features/mr-bloom/components/molecules/ChatComposer.svelte` (`handleSubmit` / `onsubmit`) |
| Store | `src/lib/features/mr-bloom/stores/mrBloomStore.ts` |
| API client | `src/lib/api.ts` |
| Message rendering | `src/lib/features/mr-bloom/components/molecules/ChatMessage.svelte` |
| Waiting state | `src/lib/features/mr-bloom/components/atoms/LoadingDots.svelte` (driven by `isWaitingForResponse` in `mrBloomStore`) |
| Auto-scroll | `src/lib/features/mr-bloom/components/organisms/MrBloomConversationPanel.svelte` (`messagesContainer.scrollTop = messagesContainer.scrollHeight` inside an `$effect`) |
| Widget | `src/lib/features/companion-widget/components/organisms/CompanionWidget.svelte` |

## Test Coverage

| Test ID | Test function | Behavior | Result |
|---|---|---|---|
| UI-001 | `UI-001: Renders conversation UI` | Proves conversation UI renders input and send controls. | PASS |
| UI-002 | `UI-002, UI-003...: Message lifecycle and sending` | Types input and triggers send. Simulates API resolve to verify full message roundtrip. | PASS |
| UI-003 | `UI-002, UI-003...: Message lifecycle and sending` | Verifies the rendered user message element count is exactly 1 before and after API resolution (no optimistic hydration duplication). | PASS |
| UI-004 | `UI-002, UI-003...: Message lifecycle and sending` | Keyboard Enter triggers exactly 1 API call and clears input. | PASS |
| UI-005 | `ChatComposer does not submit on Shift+Enter and inserts newline` | Shift+Enter does not trigger submit and explicitly inserts `\n` via native behavior. | PASS |
| UI-006 | `ChatComposer does not submit when composing (IME)...` | Enter keydown with `isComposing: true` is ignored. Enter with `isComposing: false` submits correctly. | PASS |
| UI-007 | `UI-002, UI-003...: Message lifecycle and sending` | Verifies `isWaitingForResponse` true during deferred API request, then false upon resolution. | PASS |
| UI-011 | `UI-002, UI-003...: Message lifecycle and sending` | Verifies exact DOM ordering (`.bubble` index 0 = user, index 1 = assistant). | PASS |
| UI-013 | `UI-013: Auto-scroll` | Appending a message triggers `tick()` which writes `messagesContainer.scrollHeight` to `scrollTop`. | PASS |
| UI-020 | `UI-020: Widget does not expose free-form chat composer` | Verifies absence of main textbox and `Send` button in `CompanionWidget`. | PASS |

## RED → GREEN
No production defects discovered. Existing behavior already satisfied this block; regression coverage was added via Svelte DOM/Vitest integration testing.

## Keyboard Matrix
| Input | Composing | Expected | Tested Behavior |
|---|---:|---|---|
| Enter | No | Send | Submits form. |
| Shift+Enter | No | Newline, no send | `value` updates with `\n`, `onsubmit` not called. |
| Enter | Yes | No send | `onsubmit` not called. |
| Enter after compositionend | No | Send | `onsubmit` called correctly with payload. |

## Message Lifecycle
- **User message rendered count:** Exactly 1 (no optimistic duplication after API resolve).
- **API/send invocation count:** Exactly 1 call to `api.post('/assistant/chat')`.
- **Waiting state while pending:** Store explicitly reports `isWaitingForResponse = true`. The `LoadingDots` component renders with an explicit accessible `role="status"` and `aria-label="Waiting for response"` which is successfully queried in the DOM.
- **Final message order:** User message strictly preceeds Assistant response in DOM.
- **Waiting state after resolution:** Store explicitly reports `isWaitingForResponse = false` and the accessible `role="status"` element correctly unmounts from the DOM.

## Auto-scroll evidence
- **scroll mechanism used by production:** Assignment to `messagesContainer.scrollTop = messagesContainer.scrollHeight` inside an `$effect`.
- **event/state change triggering scroll:** Changes in `chatHistory.length` or `isWaitingForResponse`.
- **test evidence:** Appending a message into `mrBloomStore` triggers Svelte's reactive tick, causing the mocked `scrollTop` value to correctly align with `scrollHeight` (500), deterministically synchronized using `waitFor` to assert the final layout behavior without arbitrary timing hacks.

## Widget Boundary
- `CompanionWidget` was explicitly tested for `queryByRole('textbox')` and `queryByRole('button', { name: 'Send' })`. Both were proven `null`, ensuring free-form composer absence.
