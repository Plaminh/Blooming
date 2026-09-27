# Implementation Plan: Mr. Bloom Planning and Draft Review Flow

**Branch**: `main` | **Date**: 2026-09-14 | **Spec**: [spec.md](./spec.md)

## Summary

Implement the four cohesive states of the Mr. Bloom planning and draft-review flow using local deterministic mock data and the existing SvelteKit and Tauri architecture.

## Technical Context

**Language/Version**: TypeScript 5, Node, Rust (Tauri)
**Primary Dependencies**: SvelteKit 2, Vite, Tauri 2
**Storage**: Local memory (Svelte Store) for mock implementation
**Testing**: Vitest for component and logic tests
**Target Platform**: Desktop (Windows/Linux via Tauri)
**Project Type**: Desktop application frontend
**Performance Goals**: Instant UI updates for local draft transitions
**Constraints**: Do not introduce real backend AI or DB integration
**Scale/Scope**: Four related screens operating on a shared draft model

## Constitution Check

- [x] Does the plan align with the Spec-driven development workflow?
- [x] Does the plan preserve the approved Tauri 2/Rust, SvelteKit/TypeScript/Vite boundaries?
- [x] Does deterministic application code remain authoritative while AI output is mocked?
- [x] Are explicit contracts and type safety boundaries defined?
- [x] Is the proposed implementation the simplest that satisfies the spec?
- [x] Are testable behavior and quality gates defined?
- [x] Does the UX handle states gracefully?
- [x] Are resource efficiency and platform scope strictly followed?
- [x] Are security and privacy principles respected?

## Repository Preflight

- **Current SvelteKit and Tauri structure**: Frontend is inside `frontend/` using SvelteKit (`src/routes`, `src/lib`). Tauri config in `src-tauri/`.
- **Existing routes and application shell**: Shell is defined in `frontend/src/routes/+layout.svelte`.
- **Shared title bar and sidebar**: `AppSidebar` and `DesktopTitleBar` exist in `frontend/src/lib/shared/components/organisms`.
- **Atomic Design directories and naming conventions**: Organized into `atoms`, `molecules`, `organisms` under `shared/components/` and `features/`.
- **Existing Mr. Bloom, Today, timeline, planning, and chat components**: None exist for Planning/Mr. Bloom yet. `today` exists but we should not duplicate it. We will create `features/mr-bloom/`.
- **Shared theme, typography, tokens, panels, buttons, and form controls**: Configured via CSS variables in `frontend/src/lib/shared/styles/`.
- **Existing icon and pixel-art asset renderers**: `AppIcon.svelte` (SVG) and `PlantSprite.svelte` / `SpriteRenderer.svelte` (pixel art) exist.
- **Existing frontend state-management conventions**: Svelte stores (`writable`, `derived`) within `lib/features/.../stores.ts`.
- **Existing tests and validation commands**: `vitest` configured in `vitest-setup.ts`. Commands: `npm run check`, `npm run test`.
- **Uncommitted user changes**: `AppSidebar.svelte` has an empty `onClick` handler for "MR. BLOOM" that needs updating.

## Planning Objective

Implement a single cohesive feature covering 1) Overall Mr. Bloom chat, 2) Plan draft review, 3) Today draft preview, 4) Timeline draft preview.

- **How the user moves between the four states**: By submitting chat requests (triggers transitions to Roadmap or Today drafts) and clicking action buttons (e.g., "GENERATE TIMELINE", "BACK TO TASKS"). The right panel swaps content while the left chat remains static.
- **Where shared chat and draft state lives**: A dedicated Svelte store `mrBloomStore` located in `frontend/src/lib/features/mr-bloom/store.ts`.
- **How the same tasks are rendered**: The single typed list of `DraftTask` in the store is iterated over by `TodayDraftPreview` and mapped into `TimelineEntry` elements by `TimelineDraftPreview`.
- **How selection, revision, cancellation, and acceptance remain consistent**: Components dispatch actions (e.g., `updateTaskDuration`, `discardDraft`, `acceptDraft`) to the store. The store is the single source of truth.
- **How unfinished AI is represented**: A deterministically mocked delay (`setTimeout`) inside the store resolves with hardcoded response fixtures (e.g., `mockTodayDraftResponse`).
- **How it integrates with the shell**: The `/mr-bloom` route simply renders the `PlanningWorkspace` inside the global layout. Unrelated screens are completely untouched.

## Architecture

We will create a new feature module `frontend/src/lib/features/mr-bloom/`.

### Shared Atoms
- **Pixel/icon renderer**: Reuse `shared/components/atoms/AppIcon.svelte` and `SpriteRenderer.svelte`.
- **Avatar**: Create `features/mr-bloom/components/atoms/ChatAvatar.svelte`.
- **Icon button**: Create `features/mr-bloom/components/atoms/IconButton.svelte`.
- **Window-control button**: Reuse existing from `DesktopTitleBar`.
- **Tab or navigation button**: Reuse existing `SidebarNavigationItem`.
- **Status badge**: Create `features/mr-bloom/components/atoms/StatusBadge.svelte` (for Core/Optional).
- **Timeline marker**: Create `features/mr-bloom/components/atoms/TimelineMarker.svelte`.
- **Divider**: Create `features/mr-bloom/components/atoms/Divider.svelte`.
- **Text input**: Create `features/mr-bloom/components/atoms/TextInput.svelte`.
- **Primary and secondary buttons**: Create `features/mr-bloom/components/atoms/ActionButton.svelte`.
- **Loading indicator**: Create `features/mr-bloom/components/atoms/LoadingDots.svelte`.

### Molecules
- **Sidebar navigation item**: Reuse `SidebarNavigationItem.svelte`.
- **Chat message**: Create `ChatMessage.svelte` (Avatar + bubble).
- **Prompt suggestion**: Create `PromptSuggestion.svelte` (The large "PLAN MY DAY" buttons).
- **Chat composer**: Create `ChatComposer.svelte` (Input + Send button).
- **Draft status indicator**: Create `DraftStatusIndicator.svelte`.
- **Draft task summary**: Create `DraftTaskSummary.svelte` (Row with task details and duration editor).
- **Preview tab selector**: (Not explicitly visible, but if needed, `PreviewTab.svelte`).
- **Date navigator**: Create `DateNavigator.svelte` (for Roadmap target dates).
- **Timeline hour label**: Create `TimelineHourLabel.svelte`.
- **Timeline task summary**: Create `TimelineTaskSummary.svelte` (Card on timeline).
- **Draft action group**: Create `DraftActionGroup.svelte` (Bottom buttons).

### Organisms
- **Mr. Bloom conversation panel**: `MrBloomConversationPanel.svelte`.
- **Plan draft panel**: `PlanDraftPreview.svelte`.
- **Today draft preview**: `TodayDraftPreview.svelte`.
- **Timeline draft preview**: `TimelineDraftPreview.svelte`.
- **Draft review header**: `DraftReviewHeader.svelte`.
- **Draft review action bar**: `DraftReviewActionBar.svelte`.
- **Planning workspace**: `PlanningWorkspace.svelte` (Main split layout).

### Page/template layer
- Route: `frontend/src/routes/mr-bloom/+page.svelte`
- Reuses `+layout.svelte`. Initializes store and mounts `PlanningWorkspace`.

## State and Data Model

See [data-model.md](./data-model.md) for full types.

- **Stable identifiers**: All tasks possess a `taskId` UUID.
- **One source of truth**: Draft store holds `tasks: DraftTask[]`.
- **Derived representations**: Timeline derives from `tasks` by adding start/end times and break blocks.
- **No disconnected copies**: Editing a task in Today Draft modifies the store, automatically updating Timeline.
- **No speculative types**: Types exactly match the frontend needs.

## Interaction Plan

- **Opening conversation**: Visit `/mr-bloom`. Store initializes empty draft, default greeting.
- **Entering/submitting request**: `ChatComposer` handles input. Enter key and click submit.
- **Preventing empty submissions**: Button disabled and Enter key ignored if input `.trim()` is empty.
- **Displaying messages**: Appended to `chatHistory` array.
- **Showing deterministic local response**: On submit, wait 800ms, append mock assistant message.
- **Creating a local plan draft**: Mock response assigns `activeDraft` in store.
- **Opening each draft preview**: Right panel reactivity swaps component based on `activeDraft.type`.
- **Switching preview modes**: Clicking "GENERATE TIMELINE" changes `previewMode` state variable, keeping `activeDraft` data.
- **Selecting tasks**: Supported via CSS active states on `DraftTaskSummary`.
- **Revising locally**: Duration `<input>` binds to task model.
- **Cancelling**: "DISCARD" resets `activeDraft` to `null`.
- **Accepting**: "SAVE TO X" clears draft, adds success message to chat.
- **Visible feedback**: Loading dots in chat bubble when waiting.
- **Keyboard/Accessbility**: standard HTML focus outline, `aria-label`s on icon buttons.
- **Window controls**: Inherited from Tauri shell.

## Visual Implementation Plan

### `chat-overall.png`
- **Native viewport**: ~1024x768.
- **Grid**: Left 45%, Right 55%.
- **Typography**: Header uppercase pixel, body standard Bloom font.
- **Spacing**: 20px gaps, 24px panel padding.
- **Borders/Colors**: Panel border `#cfc9b9`, light cream background.

### `plan-draft.png`
- **Panel hierarchy**: Timeline tree on the right.
- **Selected states**: Milestone cards hover outline.

### `today-draft.png`
- **Alignments**: Flexbox for task rows.
- **Inputs**: Spinbutton styling for durations.

### `timeline-draft.png`
- **Scroll behavior**: Right panel scrolls independently if timeline exceeds height.
- **Timeline rendering**: Left border dashed/solid indicating active/past.

## Asset Strategy

1. **Existing reusable runtime asset**: `leaf-icon.png` (widget).
2. **Existing reusable icon/component**: `AppIcon.svelte`.
3. **Simple control**: Edit pencil, X close, send paper plane, calendar, book, shoes, fork/knife. We will implement these via inline `<svg>` in a dedicated `features/mr-bloom/components/atoms/svg` folder if they are missing from `AppIcon`.
4. **Missing decorative**: Mr. Bloom robot avatar and Potted Plant. We will assume they exist in `/static/assets/`, or document them as `<div class="placeholder">` if absent.

## Testing Strategy

- **Chat message submission**: Component test ensuring `ChatComposer` dispatches submit.
- **Empty-message validation**: Assert submit is not dispatched for "   ".
- **Deterministic draft generation**: Unit test `mrBloomStore.ts` `submitMessage` to verify state transitions.
- **Preview-mode switching**: Assert state variable changes when timeline is requested.
- **Shared draft consistency**: Test modifying duration updates the store.
- **Cancellation**: Assert store resets on discard.
- **Draft acceptance**: Assert success message appended.
- **Accessibility**: Ensure roles and aria-labels exist.

## Visual Verification

1. Build and type-check: `npm run check`.
2. Run tests: `npm run test`.
3. Render every reference state at native viewport by running `npm run tauri dev`.
4. Capture 4 screenshots for each state.
5. Compare side by side with references.
6. Fix layout, typography, asset, spacing, and color mismatches.
7. Repeat until no major mismatch.
8. Verify no console/terminal errors.
9. Confirm no imports from `removed reference artwork`.

## Plan Deliverables

- **Exact existing file paths to reuse**:
  - `frontend/src/routes/+layout.svelte`
  - `frontend/src/lib/shared/components/organisms/AppSidebar.svelte`
  - `frontend/src/lib/shared/components/atoms/AppIcon.svelte`
- **Exact proposed file paths**:
  - `frontend/src/routes/mr-bloom/+page.svelte`
  - `frontend/src/lib/features/mr-bloom/stores/mrBloomStore.ts`
- **Components to create**:
  - All listed Atoms, Molecules, Organisms under `features/mr-bloom/components/`.
- **Components to modify**:
  - `frontend/src/lib/shared/components/organisms/AppSidebar.svelte` (update onClick).
- **Components that must remain unchanged**:
  - Any component inside `features/today/`, `features/goals/`, `shared/styles/`.
- **Implementation order**:
  1. Store & Data Model
  2. Atoms & SVGs
  3. Molecules (Composer, Task Summaries)
  4. Organisms (Chat Panel, Draft Previews)
  5. Route integration & Sidebar update
- **Testing order**:
  1. Store Unit Tests
  2. Component Integration Tests
  3. Visual Verification
- **Visual-verification procedure**: Described above.
- **Known risks and mitigation**:
  - Risk: Missing pixel-art SVGs. Mitigation: Use CSS placeholders heavily labeled as such.
- **Explicit out-of-scope items**:
  - Real backend endpoints.
  - Actual persistence to SQLite/Postgres.
  - Animations (unless strictly implied).
