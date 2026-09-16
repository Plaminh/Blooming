# Quickstart Validation Guide: Frontend Architecture Cleanup

This guide provides runnable validation scenarios to prove the frontend architectural cleanup works end-to-end without regressions.

## Prerequisites

- Node.js environment with dependencies installed.
- Rust and Tauri prerequisites for desktop testing.

## Automated Verification

Run the configured type, test and build checks. No separate formatting or lint script is configured.

```bash
cd frontend
npm run check
npm run test
npm run build
cd ..
git diff --check
```

**Expected Outcome**: All commands must exit with code `0`. Any failing command must be investigated to ensure it is not a regression caused by the cleanup.

## Manual Route and Visual Verification

Due to the limitations of JSDOM in verifying layout persistence across navigations without a full E2E framework (FR-014), manual verification is required.

### 1. Persistent Layout Validation

1. Start the development server: `npm run dev` (or `npm run tauri dev`).
2. Open the application and navigate to the **Today** screen.
3. Observe the Sidebar and the Desktop Application Shell.
4. Click on **Goals** in the sidebar.
5. **Expected Outcome**: The main content area updates, but the Sidebar and the main Application Shell do **not** flash, unmount, or remount. The Garden panel on the right rail should also persist seamlessly without a visible reset.
6. Navigate back to **Today** and repeat those observations. Confirm the Today Garden position, and measure the Goals Garden at 270px high with 8px bottom spacing inside its grid (in addition to the outer padding).

### 2. Standalone Route Isolation

1. Directly load `/auth` in the browser URL bar.
2. **Expected Outcome**: Authentication renders outside the persistent `(app)` layout, with its own existing desktop shell and no sidebar or Garden.
3. Directly load `/onboarding-preview`, `/widget` and `/widget-preview`.
4. **Expected Outcome**: Onboarding also uses its own shell without a sidebar; both widget routes render without the app shell, sidebar or Garden.

### 3. Visual and Thematic Regressions

1. Navigate to **Today**, **Goals**, **Mr. Bloom**, **Settings**, and **Statistics**.
2. Compare the screens against the approved reference images in `design-assets/references/`.
3. **Expected Outcome**: 
   - No missing icons or empty rounded-square fallbacks.
   - All colors match the approved palette exactly.
   - The Garden panel background has no exposed strips or invalid crops.
   - The Mr. Bloom chat bubbles use content-driven height without excessive blank space, and timestamps align correctly.
4. Compare GoalStatusBadge, TaskStatusBadge, Add Task and Add Milestone against their pre-refactor references, including labels, hover and keyboard focus. The requested CSS values are recorded in `plan.md`.
5. Exercise short, newline-containing and long chat messages for both roles, including scrolling through all long content. Check timestamp placement. Current newline characters collapse to spaces visually; do not mistake a DOM newline assertion for preserved visual line breaks.
6. Open and close the Goals dialog, reopen it and navigate away. Confirm no stale overlay remains.

## Recorded status

See `plan.md` for actual command exit codes, warnings, Edge browser measurements and limited screenshot inspection. The complete manual checklist remains **NOT VERIFIED MANUALLY** (T027 unchecked). No claim of Tauri validation, frame-by-frame flash absence or approved-reference screenshot parity is made.
