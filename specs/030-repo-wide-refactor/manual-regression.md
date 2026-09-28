# Manual Regression Baseline

These scenarios must be manually executed before claiming the baseline is fully verified.

### Authentication
- **ID**: MAN-001
- **Feature**: Authentication
- **Preconditions**: User is logged out.
- **Input / Actions**: Navigate to `/`, enter valid credentials, click Login.
- **Expected Result**: User is authenticated and navigated to `/today`.
- **Actual Result**: N/A
- **Status**: NOT RUN
- **Known Bug Reference**: None

### Onboarding / Settings
- **ID**: MAN-002
- **Feature**: Onboarding / Settings
- **Preconditions**: User is authenticated, has not completed onboarding.
- **Input / Actions**: Complete onboarding wizard, save timezone and focus/break defaults, widget preferences. Reload/persistence check.
- **Expected Result**: Preferences persist correctly and user lands on `/today`.
- **Actual Result**: N/A
- **Status**: NOT RUN
- **Known Bug Reference**: None

### Today Plan
- **ID**: MAN-003
- **Feature**: Today Plan
- **Preconditions**: User is on `/today`.
- **Input / Actions**: Input natural-language task, view draft creation, edit draft, view timeline preview, save plan, reload saved Today Plan.
- **Expected Result**: Plan saves successfully, timeline matches draft across reloads.
- **Actual Result**: N/A
- **Status**: NOT RUN
- **Known Bug Reference**: BUG-001, BUG-002

### Mr. Bloom Chat
- **ID**: MAN-004
- **Feature**: Mr. Bloom Chat
- **Preconditions**: User is on `/mr-bloom`.
- **Input / Actions**: Send normal message, deterministic request, follow clarification flow, quick reply `send_text`, apply patch, explicit action, retry failed message, test Today draft and Roadmap draft generation.
- **Expected Result**: Chat routes appropriately, patches apply correctly, failed messages retry gracefully, drafts generated successfully.
- **Actual Result**: N/A
- **Status**: NOT RUN
- **Known Bug Reference**: BUG-001

### Goals
- **ID**: MAN-005
- **Feature**: Goals
- **Preconditions**: User is on `/goals`.
- **Input / Actions**: Create new goal with Mr. Bloom, save roadmap, view goal, edit goal, verify milestone behavior.
- **Expected Result**: Goal is saved, roadmap displays correctly, milestone updates behave as expected.
- **Actual Result**: N/A
- **Status**: NOT RUN
- **Known Bug Reference**: None

### Pomodoro
- **ID**: MAN-006
- **Feature**: Pomodoro
- **Preconditions**: User has an active task.
- **Input / Actions**: Start timer, pause, resume, finish.
- **Expected Result**: Timer behaves correctly, result is persisted as a FocusRun.
- **Actual Result**: N/A
- **Status**: NOT RUN
- **Known Bug Reference**: None

### Re-plan
- **ID**: MAN-007
- **Feature**: Re-plan
- **Preconditions**: User has completed a pomodoro on a task.
- **Input / Actions**: Trigger re-plan. Check unfinished work behavior, check completed work remains preserved, check re-plan after focus outcome.
- **Expected Result**: Unfinished work is adjusted, completed work is preserved.
- **Actual Result**: N/A
- **Status**: NOT RUN
- **Known Bug Reference**: None

### Garden
- **ID**: MAN-008
- **Feature**: Garden
- **Preconditions**: User has completed a pomodoro.
- **Input / Actions**: Visit `/garden`, check water/leaves balance, unlock plant, select plant, reload persisted state.
- **Expected Result**: Rewards are accrued correctly, plant unlocks successfully, and selected plant persists on reload.
- **Actual Result**: N/A
- **Status**: NOT RUN
- **Known Bug Reference**: None

### Widget
- **ID**: MAN-009
- **Feature**: Widget
- **Preconditions**: Tauri widget is enabled.
- **Input / Actions**: Show/hide widget, observe clock, focus timer state, reminder state, sync with main app.
- **Expected Result**: Widget accurately reflects main application state in real-time.
- **Actual Result**: N/A
- **Status**: NOT RUN
- **Known Bug Reference**: None
