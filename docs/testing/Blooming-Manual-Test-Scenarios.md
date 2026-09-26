# Blooming MVP — Manual Testing Specification (Non-Chat Features)

> **Document Version:** 1.0.0  
> **Status:** Authoritative Manual Test Specification  
> **Target Scope:** All Blooming MVP features excluding the Mr. Bloom natural-language chatbox/planning-chat system.  
> **Application Version:** 0.1.0 (Desktop Tauri 2 / SvelteKit / FastAPI / PostgreSQL)

---

## 1. Test Environment & Execution Guidelines

### 1.1 Test Accounts & State Isolation
To prevent cross-scenario data contamination and preserve ledger invariants, adhere strictly to these principles:
- **Primary Test Account (`User A`):** `tester.primary@blooming.test` / `Password123!` (Clean, verified account used for happy-path and sequential blocks).
- **Secondary Test Account (`User B`):** `tester.secondary@blooming.test` / `Password123!` (Used strictly for user isolation and security boundary testing).
- **Transient Accounts:** Created dynamically for registration, unverified login, and token expiration scenarios.
- **Ledger Invariant Warning:** Reward events in `reward_events` are append-only with strict unique `idempotency_key` constraints. Do NOT attempt to manually mutate or delete individual rows in the ledger during testing; use fresh test accounts when ledger baseline reset is required.

### 1.2 Timezone & Clock Context
- **Default Test Timezone:** `UTC` or local client timezone matching system clock.
- **Time Sensitivity:** Do NOT hardcode historical timestamps. Always use relative timestamps (e.g., `Now + 10 minutes`, `Tomorrow at 09:00`, `Current Date`) to ensure deterministic evaluation regardless of test execution date.
- **Date Rollover:** In multi-day or planning boundary scenarios, observe the local midnight transition according to the active snapshot timezone configured in `user_settings.timezone`.

### 1.3 Execution Environments
Every scenario specifies its execution environment:
- **Tauri Desktop Only:** Requires the compiled desktop binary or `npm run tauri dev`. Tests native window controls, system tray icons, always-on-top attributes, autostart plugins, and desktop reminder background timers.
- **Web Only:** Executable in a standard web browser pointing to `http://localhost:5173` or Vite dev server.
- **Either:** Behavior is identical in Web browser and Desktop webview.

### 1.4 Verification Layers
Each test specifies three verification checkpoints:
1. **UI:** Visual feedback, toasts, sprite changes, countdown timers, button states.
2. **Network/API:** HTTP status codes, payload structures in Browser DevTools Network tab.
3. **DB:** Authoritative database rows queried via PostgreSQL `psql` or database GUI.

---

## 2. Test Scenarios

### Group 1: Authentication & Account

#### AUTH-01 — Register New Account and Dispatch Verification Token
**Priority:** Core  
**Environment:** Either  
**Precondition:**  
- Backend server and database are running.
- Test email `new.gardener@blooming.test` is not registered in the database.

**Actions:**
1. Navigate to `/auth`.
2. Toggle from "SIGN IN" to "REGISTER".
3. Enter email `new.gardener@blooming.test` and password `SecurePassword123!`.
4. Click the register button.

**Expected output:**
- UI displays a notification prompting the user to check their email for verification.
- User is NOT immediately logged in or redirected to the dashboard.
- A new record is created in `users` with `account_status = 'ACTIVE'` and `email_verified_at IS NULL`.
- A row is created in `user_settings` with default values (timezone `'UTC'`, focus `25`, break `5`).
- A single-use verification token is generated in `email_verification_tokens`.

**Verification:**
- **UI:** Registration success state rendered; form inputs reset or locked.
- **Network/API:** `POST /api/v1/auth/register` returns `HTTP 201 Created` with `{"email": "new.gardener@blooming.test", "verification_required": true}`.
- **DB:** `SELECT email, email_verified_at, account_status FROM users WHERE email = 'new.gardener@blooming.test';` returns 1 row with `NULL` verified timestamp.

**Cleanup:**
- Retain account for `AUTH-03` or delete user via database cascading delete if testing in isolation.

---

#### AUTH-02 — Prevent Duplicate Registration with Case-Insensitive Email
**Priority:** High  
**Environment:** Either  
**Precondition:**  
- Account `new.gardener@blooming.test` already exists in database.

**Actions:**
1. Navigate to `/auth` registration tab.
2. Enter email in uppercase/mixed case: `NEW.GARDENER@BLOOMING.TEST`.
3. Enter password `AnotherPassword123!`.
4. Click register button.

**Expected output:**
- UI displays an error banner: "Email already registered." or conflict error.
- No duplicate user row is inserted.

**Verification:**
- **UI:** Error message visible, no navigation away from `/auth`.
- **Network/API:** `POST /api/v1/auth/register` returns `HTTP 409 Conflict` with `detail: "Email already registered."`.
- **DB:** `SELECT count(*) FROM users WHERE LOWER(email) = 'new.gardener@blooming.test';` returns exactly `1`.

**Cleanup:**
- None required.

---

#### AUTH-03 — Verify Email with Valid Token and Auto-Provision Starter Garden
**Priority:** Core  
**Environment:** Either  
**Precondition:**  
- User `new.gardener@blooming.test` registered but unverified.
- Retrieve the valid `raw_token` generated during registration or query token hash from `email_verification_tokens`.

**Actions:**
1. Open browser to `/verify-email?token=<RAW_TOKEN>`.
2. Observe verification progress screen.

**Expected output:**
- UI displays "Email Verified!" and automatically stores the returned JWT access token in `localStorage.blooming_access_token`.
- User is automatically redirected to `/onboarding`.
- Database updates `users.email_verified_at` with current UTC timestamp and marks token `used_at`.

**Verification:**
- **UI:** Card indicates success and redirects to `/onboarding` within 2 seconds.
- **Network/API:** `POST /api/v1/auth/verify-email` returns `HTTP 200 OK` with `{"access_token": "...", "token_type": "bearer"}`.
- **DB:** `SELECT email_verified_at FROM users WHERE email = 'new.gardener@blooming.test';` is NOT NULL; `SELECT used_at FROM email_verification_tokens WHERE user_id = (SELECT id FROM users WHERE email = 'new.gardener@blooming.test');` is NOT NULL.

**Cleanup:**
- Retain verified user for onboarding test `ONBOARD-01`.

---

#### AUTH-04 — Reject Email Verification with Invalid or Expired Token
**Priority:** High  
**Environment:** Either  
**Precondition:**  
- None.

**Actions:**
1. Navigate to `/verify-email?token=invalid_dummy_token_99999`.
2. Wait for API response.

**Expected output:**
- UI displays "Link Expired" / "The verification link is invalid or has expired."
- A "Return to Login" button is visible linking back to `/auth`.
- No authentication token is placed in `localStorage`.

**Verification:**
- **UI:** Expired error message rendered; no auto-redirect.
- **Network/API:** `POST /api/v1/auth/verify-email` returns `HTTP 400 Bad Request` with `detail: "Invalid or expired token"`.
- **DB:** No user record modified.

**Cleanup:**
- None.

---

#### AUTH-05 — Login with Verified Account and Rejection on Unverified Account
**Priority:** Core  
**Environment:** Either  
**Precondition:**  
- Account `verified.user@blooming.test` is verified.
- Account `unverified.user@blooming.test` is registered but unverified (`email_verified_at IS NULL`).

**Actions:**
1. Navigate to `/auth`.
2. Attempt login with `unverified.user@blooming.test` and correct password.
3. Observe outcome.
4. Attempt login with `verified.user@blooming.test` and correct password.
5. Observe outcome.

**Expected output:**
- Step 2-3: Login fails with `HTTP 403 Forbidden` (`EMAIL_NOT_VERIFIED`). UI displays verification required warning.
- Step 4-5: Login succeeds with `HTTP 200 OK`. Access token is saved to `localStorage`, and app navigates to `/today`.

**Verification:**
- **UI:** Unverified shows error banner; verified transitions seamlessly to `/today`.
- **Network/API:** Unverified receives `HTTP 403` with `detail: "EMAIL_NOT_VERIFIED"`. Verified receives `HTTP 200` with JWT bearer token.
- **DB:** `SELECT last_login_at FROM users WHERE email = 'verified.user@blooming.test';` is updated to current time.

**Cleanup:**
- None.

---

#### AUTH-06 — Logout and Client State Eviction
**Priority:** High  
**Environment:** Either  
**Precondition:**  
- User is logged in on `/today`.

**Actions:**
1. Click `SETTINGS` in sidebar navigation.
2. In the "ACCOUNT" panel, locate "Signed in as <email>".
3. Click the `LOGOUT` button.

**Expected output:**
- Client removes `blooming_access_token` from `localStorage`.
- Window redirects immediately to `/auth`.
- Attempting to press browser Back button or manually navigating to `/today` immediately bounces user back to `/auth`.

**Verification:**
- **UI:** Redirected to login form.
- **Network/API:** Subsequent protected requests return `HTTP 401 Unauthorized`.
- **Client Storage:** `localStorage.getItem('blooming_access_token')` is `null`.

**Cleanup:**
- None.

---

### Group 2: Onboarding & Settings

#### ONBOARD-01 — Complete First-Time Onboarding Setup
**Priority:** Core  
**Environment:** Either  
**Precondition:**  
- User has verified email and arrives at `/onboarding`.
- Initial settings in DB have default values (`Mr. Bloom`, `UTC`, `25/5`).

**Actions:**
1. On `/onboarding`, observe pre-detected timezone.
2. Change Mr. Bloom display name to "Botanist Bloom".
3. Select Focus Preset `50 / 10`.
4. In Weather Location Picker, type "Tokyo" and select "Tokyo, Japan".
5. Toggle "Start Blooming at login" ON and "Keep widget on top" ON.
6. Click "Start Blooming" (Finish).

**Expected output:**
- Form saves all options to backend via `PUT /me/settings`.
- App navigates to `/today`.
- Widget and desktop settings are signaled via desktop event `blooming:settings-updated`.

**Verification:**
- **UI:** Seamless redirect to `/today`.
- **Network/API:** `PUT /api/v1/me/settings` payload contains `mr_bloom_display_name: "Botanist Bloom"`, `default_focus_minutes: 50`, `default_break_minutes: 10`, `weather_location_name: "Tokyo, Japan"`, `launch_on_startup: true`, `widget_always_on_top: true`. Response is `HTTP 200 OK`.
- **DB:** `SELECT mr_bloom_display_name, default_focus_minutes, weather_location_name FROM user_settings WHERE user_id = <USER_ID>;` reflects Tokyo, 50, Botanist Bloom.

**Cleanup:**
- Retain settings for subsequent tests.

---

#### SETTINGS-01 — Update Focus and Break Duration Bounds Validation
**Priority:** High  
**Environment:** Either  
**Precondition:**  
- User is logged in and navigates to `/settings`.

**Actions:**
1. In the "FOCUS TIMER" panel, change focus minutes to `0`. Observe UI validation.
2. Change focus minutes to `721`. Observe UI validation.
3. Change focus minutes to `45`.
4. Change break minutes to `-1`. Observe UI validation.
5. Change break minutes to `181`. Observe UI validation.
6. Change break minutes to `15`.
7. Click `SAVE CHANGES`.

**Expected output:**
- Values outside [1, 720] for focus or [0, 180] for break trigger inline validation errors preventing form submission.
- Valid values (45 / 15) save successfully with a confirmation message.

**Verification:**
- **UI:** Inline error message displayed when invalid; "Changes saved successfully" toast appears on valid save.
- **Network/API:** `PUT /api/v1/me/settings` returns `HTTP 200 OK` with `default_focus_minutes: 45, default_break_minutes: 15`.
- **DB:** `user_settings` table reflects `default_focus_minutes = 45` and `default_break_minutes = 15`.

**Cleanup:**
- Reset defaults to 25 / 5 if desired.

---

#### SETTINGS-02 — Milestone Reminder Lead Time Configuration
**Priority:** Normal  
**Environment:** Either  
**Precondition:**  
- User is on `/settings`.

**Actions:**
1. Locate "NOTIFICATIONS" panel.
2. In the "Milestone reminder" dropdown, inspect choices:
   - "At the deadline" (`0`)
   - "One hour before" (`60`)
   - "One day before" (`1440`)
   - "Three days before" (`4320`)
3. Select "One hour before" (`60`).
4. Click `SAVE CHANGES`.
5. Refresh the page (`F5`).

**Expected output:**
- Setting is persisted and dropdown still shows "One hour before" after reload.

**Verification:**
- **UI:** Dropdown value is 60 after refresh.
- **Network/API:** `PUT /api/v1/me/settings` includes `milestone_reminder_lead_time_minutes: 60`.
- **DB:** `SELECT milestone_reminder_lead_time_minutes FROM user_settings WHERE user_id = <USER_ID>;` equals `60`.

**Cleanup:**
- Revert dropdown to "One day before" (1440).

---

#### SETTINGS-03 — Quiet Hours Configuration via Backend API *(Implementation Gap)*
**Priority:** High  
**Environment:** Either  
**Precondition:**  
- User is logged in with access token available.
- *(Note: Frontend `NotificationsPanel.svelte` currently omits quiet hours inputs; test executes via API to verify backend authority and constraint enforcement).*

**Actions:**
1. Execute `PUT /api/v1/me/settings` with payload:
   ```json
   {
     "quiet_hours_enabled": true,
     "quiet_hours_start": "22:00:00",
     "quiet_hours_end": "08:00:00"
   }
   ```
2. Verify response.
3. Execute `PUT /api/v1/me/settings` with invalid asymmetric pair:
   ```json
   {
     "quiet_hours_start": "22:00:00",
     "quiet_hours_end": null
   }
   ```

**Expected output:**
- Action 1 succeeds: Database sets quiet hours pair and enabled flag.
- Action 3 fails: Database check constraint `user_settings_quiet_hours_pair` rejects single null and returns HTTP 422/400.

**Verification:**
- **Network/API:** Action 1 returns `HTTP 200 OK`. Action 3 returns `HTTP 400/422`.
- **DB:** `SELECT quiet_hours_enabled, quiet_hours_start, quiet_hours_end FROM user_settings WHERE user_id = <USER_ID>;` shows `t`, `22:00:00`, `08:00:00`.

**Cleanup:**
- Reset `quiet_hours_enabled` to `false`.

---

#### SETTINGS-04 — Weather Location Geocoding Search and Selection
**Priority:** Core  
**Environment:** Either  
**Precondition:**  
- User is on `/settings` "GENERAL" panel.

**Actions:**
1. In the "Weather Location" input, type "Lon" (at least 2 characters).
2. Observe autocomplete dropdown list.
3. Select "London, Greater London, United Kingdom".
4. Ensure "Show local weather in widget" toggle is ON.
5. Click `SAVE CHANGES`.

**Expected output:**
- Autocomplete displays up to 5 candidates from Open-Meteo geocoding.
- Selected place fills latitude and longitude coordinates.
- Saved confirmation toast appears.

**Verification:**
- **UI:** Current location displays "Saved: London, Greater London, United Kingdom".
- **Network/API:** `GET /api/v1/weather/search?q=Lon` returns `HTTP 200 OK` with candidate array. `PUT /api/v1/me/settings` submits `weather_location_name`, `weather_lat`, and `weather_lon`.
- **DB:** Coordinates in `user_settings` are rounded to 2 decimal places (e.g., lat: 51.51, lon: -0.13).

**Cleanup:**
- None.

---

#### SETTINGS-05 — Garden Season Override Setting
**Priority:** Normal  
**Environment:** Either  
**Precondition:**  
- User is on `/settings` "GENERAL" panel.

**Actions:**
1. Locate "Garden Season Override" dropdown.
2. Change from "Auto (Based on weather/date)" to "Winter".
3. Click `SAVE CHANGES`.
4. Navigate to `/today` or inspect widget background.

**Expected output:**
- App environment store updates `sceneSeason` to `WINTER`.
- Vegetation/garden layers in widget and dashboard reflect winter vegetation regardless of real-world calendar month.

**Verification:**
- **UI:** Garden scene displays winter assets.
- **Network/API:** `PUT /api/v1/me/settings` payload contains `scene_season: "WINTER"`.
- **DB:** `SELECT scene_season FROM user_settings WHERE user_id = <USER_ID>;` equals `'WINTER'`.

**Cleanup:**
- Revert "Garden Season Override" to "AUTO".

---

#### SETTINGS-06 — Desktop Native Settings Reconciliation (Autostart & Always-on-Top)
**Priority:** High  
**Environment:** Tauri Desktop Only  
**Precondition:**  
- Blooming is running in Tauri Desktop mode.

**Actions:**
1. Open Settings in the main window.
2. Toggle "Start Blooming at login" ON.
3. Toggle "Keep widget on top" ON.
4. Click `SAVE CHANGES`.
5. Bring an external window (e.g., Notepad or Browser) to the foreground and move it over the widget.

**Expected output:**
- Tauri plugin reconciles settings via `desktop.reconcileSettings()`.
- Widget window stays visually pinned on top of the external window.
- Both toggles remain ON after restarting the desktop application.

**Verification:**
- **UI:** Widget remains above all other desktop applications.
- **Desktop API:** In DevTools console: `await window.__TAURI__.window.getCurrentWindow().isAlwaysOnTop()` returns `true`.
- **DB:** `launch_on_startup: true`, `widget_always_on_top: true` in `user_settings`.

**Cleanup:**
- Revert toggles to OFF if desired.

---

### Group 3: Today / Saved Plan UI

*Note: Chat creation of plans is excluded. Preconditions assume valid saved plans exist.*

#### TODAY-UI-01 — Empty State When No Daily Plan Exists
**Priority:** Core  
**Environment:** Either  
**Precondition:**  
- Clean test account or current date has no confirmed plan in `daily_plans`.

**Actions:**
1. Navigate to `/today`.
2. Inspect the main timeline area.
3. Inspect the right rail.

**Expected output:**
- Main area displays "No tasks scheduled for this day."
- No phantom task cards or broken time blocks appear.
- Right rail displays empty task placeholder ("Select a task to focus on it").
- Date navigation shows current day, previous day, and next day buttons.

**Verification:**
- **UI:** Empty state message visible; Start Focus button is disabled.
- **Network/API:** `GET /api/v1/today` returns `HTTP 200 OK` with `status: "NO_PLAN"`, `blocks: []`.
- **DB:** `SELECT * FROM daily_plans WHERE user_id = <USER_ID> AND plan_date = CURRENT_DATE;` returns 0 rows.

**Cleanup:**
- None.

---

#### TODAY-UI-02 — Render Saved Plan with Tasks, Breaks, and Visual Geometry
**Priority:** Core  
**Environment:** Either  
**Precondition:**  
- A valid daily plan exists for today with 2 tasks ("Draft Architecture", "Review PR") and 1 intermediate break ("Coffee Break").

**Actions:**
1. Navigate to `/today`.
2. Inspect the rendered timeline.
3. Click on the first task card ("Draft Architecture").

**Expected output:**
- Timeline renders continuous hour markers with vertical axis line.
- Red/accent horizontal line represents current time marker if within schedule range.
- Tasks appear at their scheduled positions with duration strings (e.g., `(45 min)`).
- Break block appears with break coffee/cup icon and distinct styling.
- Clicking "Draft Architecture" highlights the card and loads its details into the Right Rail.

**Verification:**
- **UI:** Card selected state active; Right Rail displays "Draft Architecture", priority, category, and duration.
- **Network/API:** `GET /api/v1/today` returns `status: "CONFIRMED"` with 3 blocks in `blocks` array.
- **DB:** `SELECT id, title, block_type, status FROM plan_blocks WHERE daily_plan_id = <PLAN_ID> ORDER BY position;` matches UI cards.

**Cleanup:**
- Keep plan for Focus tests.

---

#### TODAY-UI-03 — Today Task Details Are Read-Only
**Priority:** High  
**Environment:** Either  
**Precondition:**  
- Today page displays a pending task "Draft Architecture" (45 min, Category: Work).

**Actions:**
1. Select "Draft Architecture" on the timeline.
2. Inspect the Right Rail task details panel.
3. Verify all metadata fields (title, time range, duration, category, notes).

**Expected output:**
- Right Rail shows task title as plain text heading, not an editable input.
- Time range and duration displayed as static text (e.g., "09:00 – 09:45 (45 min)").
- Category displayed as a badge, not a dropdown/select.
- Notes displayed as static text, not a textarea.
- No pencil/edit toggle icon exists anywhere in the Right Rail.
- No "EDIT MANUALLY" button exists in Bottom Actions.
- No "Save" or "Cancel" buttons exist in the Right Rail.
- No "Delete" button or action exists in the Right Rail.
- Execution actions present: "MARK COMPLETE", "ADJUST WITH MR. BLOOM", "START FOCUS".

**Verification:**
- **UI:** All task metadata is rendered as non-interactive text; no form controls exist for editing task properties.
- **Network/API:** No `PATCH /api/v1/today/tasks/<TASK_ID>` call is made when inspecting the task.

**Cleanup:**
- None.

---

#### TODAY-UI-03a — Mark Task Complete from Today
**Priority:** High  
**Environment:** Either  
**Precondition:**  
- Today page displays a pending (upcoming/active) task with a valid `task_id`.

**Actions:**
1. Select the task on the timeline.
2. In the Right Rail, click "MARK COMPLETE".

**Expected output:**
- Task status updates to "completed" in the Right Rail and on the timeline card.
- "MARK COMPLETE" button changes to "COMPLETED" and becomes disabled.
- "START FOCUS" button becomes disabled for the completed task.
- Schedule update signal `desktop.scheduleUpdated()` is emitted.

**Verification:**
- **UI:** Task card shows completed styling; MARK COMPLETE button disabled and reads "COMPLETED".
- **Network/API:** `PATCH /api/v1/today/tasks/<TASK_ID>/status` called with `{ status: "COMPLETED" }` and returns `HTTP 200 OK`.
- **DB:** `SELECT status FROM plan_blocks WHERE task_id = <TASK_ID>;` shows `COMPLETED`.

**Cleanup:**
- None.

---

#### TODAY-UI-03b — Quick Replan from Today
**Priority:** High  
**Environment:** Either  
**Precondition:**  
- Today page displays a plan with at least one uncompleted task.

**Actions:**
1. In Bottom Actions, click "QUICK REPLAN".
2. Observe the timeline refresh.

**Expected output:**
- Timeline blocks update with recalculated start/end times from current time forward.
- Completed tasks remain in their original positions.
- If any tasks overflow available time, a warning notification appears.
- Schedule update signal `desktop.scheduleUpdated()` is emitted.

**Verification:**
- **UI:** Timeline blocks reflect new scheduling; warning shown if tasks overflow.
- **Network/API:** `POST /api/v1/today/replan` called and returns updated plan with recalculated blocks.
- **DB:** `SELECT planned_start_at, planned_end_at FROM plan_blocks WHERE daily_plan_id = <PLAN_ID> AND status != 'COMPLETED' ORDER BY position;` shows updated times.

**Cleanup:**
- None.

---

#### TODAY-UI-03c — Adjust Existing Plan with Mr. Bloom
**Priority:** High  
**Environment:** Either  
**Precondition:**  
- Today page displays a saved plan with at least one task.

**Actions:**
1. Select a task on the timeline.
2. In the Right Rail, click "ADJUST WITH MR. BLOOM".
3. Observe navigation to Mr. Bloom.
4. In Mr. Bloom, verify the plan is loaded as a TodayDraft.
5. Make an edit (e.g., change task duration via chat).
6. Click "Generate Timeline" to get a scheduler preview.
7. Click "Save" to commit the updated plan.
8. Verify navigation returns to `/today`.

**Expected output:**
- Step 2-3: Browser navigates to `/mr-bloom?date=YYYY-MM-DD&taskId=<TASK_ID>`.
- Step 4: Mr. Bloom right panel shows TodayDraftPreview with tasks from the existing plan. Chat displays "Loaded plan for YYYY-MM-DD. Task selected for adjustment."
- Step 6: Scheduler generates a fresh timeline preview (preview invalidation works).
- Step 7: Plan saves via `POST /api/v1/today/save` with `replace_existing: true`.
- Step 8: Navigates back to `/today?date=YYYY-MM-DD` showing the updated schedule.

**Verification:**
- **UI:** Full round-trip: Today → Mr. Bloom (with plan loaded) → edit → preview → save → Today (updated).
- **Network/API:** `GET /api/v1/today?date=...` loads plan into draft; `POST /api/v1/today/preview` generates preview; `POST /api/v1/today/save` commits changes.
- **DB:** Plan blocks reflect the edits after save.

**Cleanup:**
- None.

---

#### TODAY-UI-04 — Date Navigation and Schedule Boundary Check
**Priority:** High  
**Environment:** Either  
**Precondition:**  
- A plan exists for today, but no plan exists for tomorrow.

**Actions:**
1. On `/today`, observe the timeline header date label.
2. Click the `>` (Next Day) button in `DateNavigation`.
3. Observe timeline update.
4. Click the `<` (Previous Day) button twice (to view Yesterday).
5. Click the "Today" shortcut / return to current date.

**Expected output:**
- Step 2-3: URL updates to `/today?date=YYYY-MM-DD` (tomorrow). Header displays tomorrow's date. Empty state "No tasks scheduled for this day." is rendered.
- Step 4: URL updates to yesterday's date.
- Step 5: URL resets to `/today` and current day's active plan re-appears without data loss.

**Verification:**
- **UI:** Correct date labels rendered for each navigation offset; "Today" button restores today's plan.
- **Network/API:** `GET /api/v1/today?date=...` called with respective ISO date strings.
- **DB:** Query verifies plans for requested dates.

**Cleanup:**
- None.

---

#### TODAY-UI-05 — Preserved Completed History Rendering on Timeline
**Priority:** Core  
**Environment:** Either  
**Precondition:**  
- A task was previously marked `COMPLETED` earlier today.
- Remaining tasks are pending/upcoming.

**Actions:**
1. Navigate to `/today`.
2. Inspect the completed task card on the timeline.
3. Click on the completed task card.

**Expected output:**
- Completed task card displays visual completion badge / checkmark and dimmed or distinct completed style.
- Right rail displays task status as "completed".
- Start Focus button is disabled for completed tasks.
- Timeline strictly retains the completed task in its original historical time slot.

**Verification:**
- **UI:** Completed task styled distinctively; Start Focus disabled.
- **Network/API:** `GET /api/v1/today` shows block `status: "COMPLETED"`.
- **DB:** `SELECT status, completed_at FROM plan_blocks WHERE id = <BLOCK_ID>;` shows `COMPLETED` and non-null timestamp.

**Cleanup:**
- None.

---

### Group 4: Pomodoro / Focus

#### FOCUS-01 — Start Default Pomodoro Session (25/5 Preset)
**Priority:** Core  
**Environment:** Tauri Desktop  
**Precondition:**  
- User is logged in.
- A saved Today plan contains an upcoming pending task "Draft System Architecture".
- Widget is open on the desktop.

**Actions:**
1. Open Today.
2. Select "Draft System Architecture".
3. Ensure preset "25/5" is highlighted.
4. Click `START FOCUS`.

**Expected output:**
- Focus starts exactly once.
- Task status changes to `in-progress`.
- Desktop widget immediately transitions to `focusing` state.
- Widget displays countdown starting at `25:00` and counts down every second.
- Start Focus button on Today page becomes disabled.
- Exactly one active focus run exists in DB with `status = 'FOCUSING'`.

**Verification:**
- **UI:** Today timeline card marked `in-progress`; Widget displays `25:00` countdown with active plant and pause button.
- **Network/API:** `POST /api/v1/focus/start` returns `HTTP 200 OK` with `planned_focus_seconds: 1500, planned_break_seconds: 300, status: "FOCUSING"`.
- **DB:** `SELECT id, status, planned_focus_seconds, started_at FROM focus_runs WHERE user_id = <USER_ID> AND status = 'FOCUSING';` returns 1 row.

**Cleanup:**
- Finish or cancel focus session via `FOCUS-03` / `FOCUS-06`.

---

#### FOCUS-02 — Start Custom Duration Focus Session
**Priority:** High  
**Environment:** Either  
**Precondition:**  
- Today plan has an upcoming task "Write Unit Tests".
- No active focus session is running.

**Actions:**
1. Select "Write Unit Tests".
2. In the Right Rail, click the "Custom" preset button.
3. Enter `15` minutes focus and `3` minutes break.
4. Click Save Custom, then click `START FOCUS`.

**Expected output:**
- Focus starts with 15 minutes planned focus (900 seconds) and 3 minutes break (180 seconds).
- Widget timer displays `15:00`.

**Verification:**
- **UI:** Countdown begins at `15:00`.
- **Network/API:** `POST /api/v1/focus/start` payload has `planned_focus_seconds: 900, planned_break_seconds: 180`.
- **DB:** `focus_runs` records `planned_focus_seconds = 900`.

**Cleanup:**
- End session.

---

#### FOCUS-03 — Pause and Resume Focus Session with Time Compensation
**Priority:** Core  
**Environment:** Tauri Desktop  
**Precondition:**  
- Active focus session is running with 25 minutes planned.
- 60 seconds have elapsed (`24:00` remaining).

**Actions:**
1. In the Widget (or via API), click the Pause button.
2. Wait 10 seconds.
3. Observe widget timer and character state.
4. Click the Resume button.
5. Observe widget timer countdown resumes.

**Expected output:**
- When paused: Countdown stops at `24:00`. Mr. Bloom displays speech "Take your time...". Focus run status becomes `PAUSED`.
- When resumed: Countdown resumes from `24:00`. `total_paused_seconds` increases by ~10 seconds. `expected_end_at` is pushed back by the paused duration.

**Verification:**
- **UI:** Timer freezes during pause; resumes smoothly on resume.
- **Network/API:** `POST /api/v1/focus/pause` returns `status: "PAUSED"`. `POST /api/v1/focus/resume` returns `status: "FOCUSING"`.
- **DB:** `SELECT status, total_paused_seconds, paused_at FROM focus_runs WHERE id = <RUN_ID>;` shows `total_paused_seconds >= 10` and `paused_at IS NULL` after resume.

**Cleanup:**
- Retain session for completion tests.

---

#### FOCUS-04 — Prevent Duplicate Active Focus Sessions
**Priority:** High  
**Environment:** Either  
**Precondition:**  
- An active focus run (`RUN A`) is already in progress (`FOCUSING` or `PAUSED`).

**Actions:**
1. Open a second browser tab or trigger an API call to start another focus session on a different task:
   `POST /api/v1/focus/start` with another `task_id`.

**Expected output:**
- Request is rejected with conflict error.
- Existing session `RUN A` remains uncorrupted and active.
- No second focus run is created.

**Verification:**
- **UI:** Error toast: "An active focus session already exists" (or HTTP 409).
- **Network/API:** Returns `HTTP 409 Conflict` (or `InvalidStatusTransitionError`).
- **DB:** `SELECT count(*) FROM focus_runs WHERE user_id = <USER_ID> AND status IN ('FOCUSING', 'PAUSED');` strictly equals `1`.

**Cleanup:**
- End `RUN A`.

---

#### FOCUS-05 — Active Session Persistence Across App Reload and Sleep/Wake
**Priority:** High  
**Environment:** Tauri Desktop  
**Precondition:**  
- Focus session is active with 20 minutes remaining.

**Actions:**
1. Close the main window (hides to tray).
2. Reload the widget page (`Ctrl+R` in dev mode) or restart the desktop app.
3. Re-open widget and main window.

**Expected output:**
- Widget immediately queries `GET /api/v1/focus/active`.
- Widget calculates remaining time from server `started_at` minus `total_paused_seconds` relative to current wall clock.
- Timer continues counting down accurately without resetting back to 25:00.

**Verification:**
- **UI:** Countdown reflects real elapsed time across reload; no duplicate run created.
- **Network/API:** `GET /api/v1/focus/active` returns active run details.
- **DB:** Run ID remains unchanged.

**Cleanup:**
- None.

---

#### FOCUS-06 — Natural Session End and Transition to Outcome Prompt
**Priority:** Core  
**Environment:** Tauri Desktop  
**Precondition:**  
- Active session running with 3 seconds remaining (or test session started with 5 seconds planned).

**Actions:**
1. Watch widget timer reach `00:00`.
2. Observe widget transition.

**Expected output:**
- When countdown hits 0, widget automatically transitions to `ending` (SESSION_RESULT) state.
- Speech bubble displays: "Session ended. What was the outcome?".
- Four action buttons appear:
  - `DONE`
  - `FINISHED EARLY`
  - `NEED MORE TIME`
  - `SKIP`

**Verification:**
- **UI:** Widget switches from timer display to outcome prompt buttons.
- **Network/API:** Focus run in DB remains in ending state waiting for user outcome confirmation.

**Cleanup:**
- Execute one of the outcome actions in Group 5.

---

### Group 5: Replanning

#### REPLAN-01 — Finish Focus with Outcome DONE
**Priority:** Core  
**Environment:** Tauri Desktop  
**Precondition:**  
- Widget is in `ending` state for task "Draft System Architecture".
- Task was scheduled for 45 minutes; plan had 2 subsequent upcoming tasks.

**Actions:**
1. On the widget, click the `DONE` button.
2. Observe widget and Today timeline.

**Expected output:**
- Focus session ends with `outcome = 'DONE'`, `status = 'ENDED'`.
- Task "Draft System Architecture" is marked `COMPLETED` with `completed_at` timestamp.
- User is awarded 1 Water (`FOCUS_COMPLETED`) and 1 Leaf (`TASK_COMPLETED`).
- Widget hides or shows confirmation text.
- Today timeline updates task to completed; remaining future tasks are preserved.

**Verification:**
- **UI:** Widget returns to idle/hidden; Today shows checkmark on completed task.
- **Network/API:** `POST /api/v1/focus/finish` with `{"outcome": "DONE", "should_replan": true}` returns `HTTP 200 OK`.
- **DB:**
  - `focus_runs.outcome = 'DONE'`.
  - `tasks.status = 'COMPLETED'`.
  - `reward_events` has 1 row with `resource_type = 'WATER'` and 1 row with `resource_type = 'LEAVES'`.

**Cleanup:**
- None.

---

#### REPLAN-02 — Finish Focus with Outcome FINISHED_EARLY
**Priority:** High  
**Environment:** Tauri Desktop  
**Precondition:**  
- Task "Write Unit Tests" was planned for 60 minutes.
- User clicks "End Session" after only 15 minutes. Widget enters `ending` state.

**Actions:**
1. In widget, click `FINISHED EARLY`.
2. Inspect Today timeline.

**Expected output:**
- Focus run saves `actual_duration_seconds ≈ 900` (15 min).
- Task marked `COMPLETED`.
- 1 Water and 1 Leaf awarded.
- Re-plan recalculates remaining flexible tasks to start earlier, optimizing free time.

**Verification:**
- **UI:** Task marked completed; subsequent tasks shifted forward if re-planned.
- **Network/API:** `POST /api/v1/focus/finish` returns `HTTP 200 OK`.
- **DB:** `focus_runs.actual_duration_seconds` reflects server-calculated ~900s; `reward_events` records water and leaf awards.

**Cleanup:**
- None.

---

#### REPLAN-03 — Finish Focus with Outcome NEED_MORE_TIME and Re-plan Future Flexible Work
**Priority:** Core  
**Environment:** Tauri Desktop  
**Precondition:**  
- Today plan has 3 tasks:
  1. "Task 1" (Active focus, overrun or unfinished).
  2. "Task 2" (Flexible upcoming).
  3. "Task 3" (Flexible upcoming).

**Actions:**
1. End focus session on Task 1 and select `NEED MORE TIME` with `should_replan: true`.
2. Refresh Today timeline.

**Expected output:**
- Task 1 remains `PENDING` (not completed, not skipped).
- 1 Water is awarded for the focus effort; Leaves are NOT awarded.
- Re-planning algorithm preserves elapsed historical time.
- Task 2 and Task 3 are shifted forward in time to accommodate remaining availability.
- A new `PlanRevision` is stored in `plan_revisions`.

**Verification:**
- **UI:** Task 1 remains pending; Task 2 and 3 have adjusted start/end times.
- **Network/API:** `POST /api/v1/focus/finish` returns `replan` object containing updated schedule blocks.
- **DB:** `SELECT count(*) FROM plan_revisions WHERE daily_plan_id = <PLAN_ID>;` increments by 1. Task 1 `completed_at` is NULL.

**Cleanup:**
- None.

---

#### REPLAN-04 — Finish Focus with Outcome SKIP
**Priority:** High  
**Environment:** Tauri Desktop  
**Precondition:**  
- Focus session is active on "Optional Documentation".

**Actions:**
1. Click End Session in widget, then click `SKIP`.
2. Observe rewards and task status.

**Expected output:**
- Task status changes to `SKIPPED`.
- Associated plan block status changes to `SKIPPED`.
- Zero (0) Water is awarded.
- Zero (0) Leaves are awarded.
- Remaining flexible work is adjusted to utilize newly freed time.

**Verification:**
- **UI:** Task card marked skipped; no reward toasts.
- **Network/API:** `POST /api/v1/focus/finish` returns `status: "ENDED", outcome: "SKIP"`.
- **DB:** `SELECT count(*) FROM reward_events WHERE source_focus_run_id = <RUN_ID>;` strictly equals `0`. `tasks.status = 'SKIPPED'`.

**Cleanup:**
- None.

---

#### REPLAN-05 — Re-planning Under Insufficient Remaining Availability (Overloaded Schedule)
**Priority:** High  
**Environment:** Either  
**Precondition:**  
- Current time is 17:00.
- Daily availability window ends at 18:00 (60 minutes left).
- Two pending tasks remain: "Heavy Refactor" (90 min) and "Final Testing" (30 min).

**Actions:**
1. Trigger re-plan via `POST /today/replan?target_date=YYYY-MM-DD` (or complete a focus run with `should_replan: true`).
2. Inspect Today page response.

**Expected output:**
- Re-planner schedules "Final Testing" or as much work as fits before 18:00.
- "Heavy Refactor" cannot fit into the remaining availability window.
- It is placed into `unscheduled_tasks` with a descriptive reason.
- Today page displays a warning toast: "1 task couldn't fit today. Your scheduled work was saved. Adjust your availability or replan."
- No completed or fixed historical blocks are deleted or moved.

**Verification:**
- **UI:** Warning banner appears with unscheduled task alert.
- **Network/API:** `POST /api/v1/today/replan` returns `unscheduled_tasks: [...]` with `reasons: [{"code": "NO_WINDOW", ...}]`.
- **DB:** `plan_blocks` contains only blocks fitting within availability windows; historical blocks preserved.

**Cleanup:**
- None.

---

### Group 6: Desktop Widget

#### WIDGET-01 — Widget Default Idle State Presentation
**Priority:** Core  
**Environment:** Tauri Desktop Only  
**Precondition:**  
- User is logged in. No focus session is active.
- Active plant in garden is Monstera Deliciosa (Sprouting).

**Actions:**
1. Open the Desktop Widget window (`/widget`).
2. Inspect rendered layout and elements.

**Expected output:**
- Widget window is compact (~680x289px) with custom title bar ("BLOOMING" with leaf logo).
- Mr. Bloom sprite is rendered in idle character pose.
- Active plant sprite (Monstera seed pot/sprout) is positioned on the desk.
- Ambient background reflects current time of day and season.
- Speech bubble displays: "Waiting for a focus session...".
- Widget has NO free-form text input box or chat interface.
- Widget does NOT initiate requests to external LLMs.

**Verification:**
- **UI:** Correct sprites, speech text, title bar controls; no chat input.
- **Network/API:** Only polling `GET /focus/active` and `GET /garden`; zero LLM endpoint requests.

**Cleanup:**
- None.

---

#### WIDGET-02 — Widget Window Controls (Drag, Minimize, Close-to-Hide)
**Priority:** High  
**Environment:** Tauri Desktop Only  
**Precondition:**  
- Widget is open on the desktop.

**Actions:**
1. Click and hold the title bar drag region (`.drag`) and drag the widget across the desktop.
2. Click the Minimize button (`_`) on the title bar.
3. Restore the widget from the Windows taskbar.
4. Click the Close button (`X`) on the widget title bar.
5. Inspect the Windows notification tray.

**Expected output:**
- Step 1: Widget moves smoothly across monitors.
- Step 2-3: Widget minimizes and restores without UI reload.
- Step 4-5: Clicking Close does NOT terminate the application process (`WindowEvent::CloseRequested` prevents close and calls `window.hide()`). Blooming tray icon remains active in the system tray.

**Verification:**
- **UI:** Window drags; close hides window rather than exiting process.
- **System:** `Blooming.exe` process continues running in Windows Task Manager.

**Cleanup:**
- Click tray icon or "Show companion" in tray context menu to restore widget.

---

#### WIDGET-03 — Double-Click Widget to Reveal and Focus Main Window
**Priority:** High  
**Environment:** Tauri Desktop Only  
**Precondition:**  
- Main window is minimized or hidden in the background.
- Widget is visible on the desktop.

**Actions:**
1. Double-click any empty background area of the widget (avoiding buttons or title bar).

**Expected output:**
- `openMainOnDoubleClick` triggers `windowService.openMainWindow()`.
- Main Blooming application window unminimizes, becomes visible, and gains system focus on top of other windows.

**Verification:**
- **UI:** Main window immediately comes to the foreground.
- **Desktop API:** Main webview window `isVisible()` returns `true`.

**Cleanup:**
- None.

---

#### WIDGET-04 — Reminder State Presentation via Widget Preview *(Implementation Gap)*
**Priority:** Normal  
**Environment:** Either  
**Precondition:**  
- *(Note: Production `widget/+page.svelte` handles focus/idle states; the full reminder panel presentation component is testable via `/widget-preview?kind=reminders`).*

**Actions:**
1. Open browser or webview to `/widget-preview?kind=reminders`.
2. Inspect the rendered widget components.

**Expected output:**
- Bell icon and header "2 REMINDERS" (or count).
- List of reminder bullet items with labels (e.g., "Milestone Due: Submit Report").
- Mr. Bloom displays alert icon badge (`ReminderAlerts`).
- Layout adheres to widget stroke, cream panel background, and navy border styling.

**Verification:**
- **UI:** Reminder list rendered inside speech bubble slot; alert badge on character.

**Cleanup:**
- None.

---

#### WIDGET-05 — Widget Behind-Schedule State Preview
**Priority:** Normal  
**Environment:** Either  
**Precondition:**  
- Open `/widget-preview?kind=behindSchedule`.

**Actions:**
1. Inspect the widget presentation.
2. Inspect available action buttons.

**Expected output:**
- Speech bubble displays schedule alert message.
- Status badge shows `ScheduleAlerts`.
- Actions provided: "Replan", "Later", or "Open".

**Verification:**
- **UI:** Behind schedule layout and actions rendered accurately.

**Cleanup:**
- None.

---

#### WIDGET-06 — Widget Offline Resilience
**Priority:** High  
**Environment:** Tauri Desktop Only  
**Precondition:**  
- Widget is open. Terminate backend server (`Ctrl+C` in backend terminal).

**Actions:**
1. Observe widget during the next polling tick (60s) or reload widget.

**Expected output:**
- Widget displays `OfflineStatus` indicator.
- Last known plant sprite is retained (does not disappear).
- No unhandled exceptions crash the webview.
- Speech bubble displays "Waiting for a focus session..." or connection warning.

**Verification:**
- **UI:** Plant stays visible; offline indicator shown; app remains responsive.
- **Network/API:** Failed fetch logs handled gracefully.

**Cleanup:**
- Restart backend server.

---

### Group 7: Reminders

#### REMINDER-01 — Automatic Milestone Reminder Scheduling Based on Lead Time
**Priority:** Core  
**Environment:** Either  
**Precondition:**  
- User settings have `milestone_reminder_lead_time_minutes = 60` (1 hour).
- Current UTC time is `2026-09-25 10:00:00`.

**Actions:**
1. Create a Goal with a Milestone titled "Complete Milestone Alpha" with `due_at = 2026-09-25 11:00:00` (1 hour from now).
2. Query the `reminders` table in the database.

**Expected output:**
- System calculates `due_at = milestone.due_at - 60 minutes = 10:00:00`.
- Because `due_at <= NOW`, reminder status is set to `DUE`.
- If milestone `due_at` had been 5 hours in the future, reminder status would be `SCHEDULED`.

**Verification:**
- **Network/API:** `GET /api/v1/reminders/due` returns this reminder in the list.
- **DB:** `SELECT status, due_at, original_due_at, message FROM reminders WHERE milestone_id = <MILESTONE_ID>;` shows `status = 'DUE'`, `due_at = 10:00:00`, `message = 'Milestone Due: Complete Milestone Alpha'`.

**Cleanup:**
- Retain reminder for action tests.

---

#### REMINDER-02 — System Tray Alert Red-Dot Indication on Due Reminder
**Priority:** High  
**Environment:** Tauri Desktop Only  
**Precondition:**  
- A reminder is in `DUE` status for the active user.
- Blooming desktop app is running with system tray visible.

**Actions:**
1. Observe the Blooming icon in the Windows notification tray.
2. Resolve or complete the reminder in the app.
3. Observe the tray icon again.

**Expected output:**
- Step 1: Root layout polling detects `dueReminders.length > 0` and calls `desktop.setTrayAlert(true)`. Tray icon updates to `icons/32x32_alert.png` (displays visible red alert dot).
- Step 2-3: After reminder is cleared, polling detects `dueReminders.length === 0` and calls `desktop.setTrayAlert(false)`. Tray icon returns to standard `icons/32x32.png`.

**Verification:**
- **UI:** System tray icon visually toggles between alert icon and normal icon.
- **Desktop API:** Rust command `set_tray_icon` invoked with `alert: true` and `alert: false`.

**Cleanup:**
- None.

---

#### REMINDER-03 — Reminder Action: CREATE_PLAN
**Priority:** Core  
**Environment:** Either  
**Precondition:**  
- A due reminder exists for "Complete Milestone Alpha".
- No daily plan exists for today yet.

**Actions:**
1. Open Goals page (`/goals`).
2. In the "DUE REMINDERS" panel on the right rail, locate "Milestone Due: Complete Milestone Alpha".
3. Click the `Create Plan` button.

**Expected output:**
- Backend executes `action_type: "CREATE_PLAN"`.
- A new Daily Plan draft is created for today's local date.
- A new Task is created: `Work on Milestone Due: Complete Milestone Alpha` (30 min, HIGH priority).
- A PlanBlock is added to the plan for this task.
- Reminder status transitions to `COMPLETED` with `completed_at` populated.
- Reminder disappears from Due Reminders panel.

**Verification:**
- **UI:** Reminder removed from Due Reminders list; Today page now displays the drafted task.
- **Network/API:** `POST /api/v1/reminders/<REMINDER_ID>/actions` with `{"action_type": "CREATE_PLAN"}` returns `HTTP 200 OK`.
- **DB:**
  - `reminders.status = 'COMPLETED'`.
  - `reminder_actions` has row with `action_type = 'CREATE_PLAN'`.
  - `daily_plans` and `tasks` contain newly created records linked to the milestone.

**Cleanup:**
- None.

---

#### REMINDER-04 — Reminder Action: MARK_COMPLETED and Leaf Award
**Priority:** Core  
**Environment:** Either  
**Precondition:**  
- A due reminder exists linked to Milestone "Draft Architecture Document".

**Actions:**
1. In the "DUE REMINDERS" panel, click `Mark Completed` on the reminder.
2. Inspect Goals page and Garden balance.

**Expected output:**
- Reminder status becomes `COMPLETED`.
- Associated Milestone status in `milestones` table updates to `COMPLETED` with `completed_at`.
- Milestone completion awards 1 Leaf (`MILESTONE_COMPLETED`) to the user's garden.
- Sidebar Leaves counter increments by 1.

**Verification:**
- **UI:** Milestone marked completed on roadmap; Leaf counter increases.
- **Network/API:** `POST /api/v1/reminders/<REMINDER_ID>/actions` returns `status: "COMPLETED"`.
- **DB:** `milestones.status = 'COMPLETED'`; `reward_events` has row with `event_type = 'MILESTONE_COMPLETED'`, `amount = 1`, `resource_type = 'LEAVES'`.

**Cleanup:**
- None.

---

#### REMINDER-05 — Reminder Actions: MOVE_MILESTONE and REMIND_LATER
**Priority:** High  
**Environment:** Either  
**Precondition:**  
- A due reminder exists for Milestone Beta.

**Actions:**
1. Click `Remind Later` on the reminder.
2. In the prompt, enter a date 2 days in the future (e.g., `2026-09-27`).
3. Click OK.
4. Verify reminder disappears from due list.
5. Create another due reminder and click `Move Milestone`. Enter a future date.

**Expected output:**
- `REMIND_LATER`: Reminder `due_at` is updated to future timestamp; status changes from `DUE` to `SCHEDULED`.
- `MOVE_MILESTONE`: Both the Milestone's `due_at` and the synchronized reminder's `due_at` are moved to the new target date.
- Both actions immediately clear the reminder from the Due Reminders panel.

**Verification:**
- **UI:** Due list empty.
- **Network/API:** `POST /api/v1/reminders/<ID>/actions` succeeds with new `new_due_at`.
- **DB:** `SELECT due_at, status FROM reminders WHERE id = <ID>;` confirms future timestamp and `SCHEDULED` status.

**Cleanup:**
- None.

---

### Group 8: Persisted Goals & Milestones

*Note: Roadmap drafting via chat is excluded. Preconditions assume goals and milestones exist.*

#### GOAL-UI-01 — View Goal List, Roadmap Nodes, and Ordered Milestones
**Priority:** Core  
**Environment:** Either  
**Precondition:**  
- User has 1 active Goal ("Master Rust Programming") with 3 sequential Milestones:
  1. "Read The Book" (Position 0, PENDING)
  2. "Build CLI Tool" (Position 1, PENDING)
  3. "Publish Crate" (Position 2, PENDING)

**Actions:**
1. Navigate to `/goals`.
2. Inspect the "MY GOALS" column.
3. Click "Master Rust Programming".
4. Inspect the "ROADMAP" panel in the center column.

**Expected output:**
- "MY GOALS" lists "Master Rust Programming" with milestone count `0/3 completed`.
- Center column displays Goal title and sequential Roadmap timeline.
- Milestones appear in strict position order (0, 1, 2) connected by roadmap node lines.
- Each milestone card displays title, target date, and status badge ("PENDING").

**Verification:**
- **UI:** Cards rendered in exact numerical position order; status badges accurate.
- **Network/API:** `GET /api/v1/goals/` returns array of goals with nested milestones.
- **DB:** `SELECT position, title FROM milestones WHERE goal_id = <GOAL_ID> ORDER BY position ASC;` matches UI.

**Cleanup:**
- Keep goal for subsequent tests.

---

#### GOAL-UI-02 — Edit Goal Title via Right Rail
**Priority:** Normal  
**Environment:** Either  
**Precondition:**  
- Goal "Master Rust Programming" selected on `/goals`.

**Actions:**
1. In the right rail, locate the Goal summary.
2. Click the `Edit` button.
3. In the browser prompt, type "Master Rust & Systems Programming" and click OK.

**Expected output:**
- Goal updates immediately in "MY GOALS" list and center panel header.
- New title persists after reloading the page.

**Verification:**
- **UI:** Header and list reflect updated title.
- **Network/API:** `PUT /api/v1/goals/<GOAL_ID>` with `{"title": "Master Rust & Systems Programming"}` returns `HTTP 200 OK`.
- **DB:** `SELECT title FROM goals WHERE id = <GOAL_ID>;` shows new title.

**Cleanup:**
- None.

---

#### GOAL-UI-03 — Milestone Status Toggle and Progress Bar Computation
**Priority:** Core  
**Environment:** Either  
**Precondition:**  
- Goal has 3 milestones, all `PENDING`. Overall progress bar shows `0%`.

**Actions:**
1. On Milestone 1 ("Read The Book"), change status dropdown from `PENDING` to `COMPLETED`.
2. Observe overall progress bar and garden counter.
3. Change status back from `COMPLETED` to `PENDING`.
4. Observe progress bar.

**Expected output:**
- Step 1: Overall progress bar updates to `33%` (1/3). Milestone 1 shows completed styling. 1 Leaf is awarded.
- Step 3: Progress bar returns to `0%`.
- Re-completing the milestone later will NOT award a second Leaf (farming prevention).

**Verification:**
- **UI:** Progress bar reflects `33%`; leaf counter increments.
- **Network/API:** `PUT /api/v1/goals/<GOAL_ID>/milestones/<MS_ID>` with `{"status": "COMPLETED"}` returns `HTTP 200 OK`.
- **DB:** `milestones.status = 'COMPLETED'`; `reward_events` has record with key `milestone_completed_<MS_ID>`.

**Cleanup:**
- None.

---

#### GOAL-UI-04 — Milestone Deadline Update and Reminder Resynchronization
**Priority:** High  
**Environment:** Either  
**Precondition:**  
- Milestone 2 has target deadline set to `2026-10-01`.

**Actions:**
1. On Milestone 2 card, edit the target date to `2026-10-15`.
2. Save changes.
3. Query `reminders` table for this milestone.

**Expected output:**
- Milestone `due_at` updates to `2026-10-15`.
- `reminders_service.sync_milestone_reminder` recalculates `due_at` for the associated reminder record automatically.

**Verification:**
- **UI:** Milestone card displays new date `Oct 15, 2026`.
- **Network/API:** `PUT /api/v1/goals/<GOAL_ID>/milestones/<MS_ID>` succeeds.
- **DB:** `SELECT due_at, original_due_at FROM reminders WHERE milestone_id = <MS_ID>;` reflects updated timestamp.

**Cleanup:**
- None.

---

#### GOAL-UI-05 — Goal Deletion via API and Cascading Cleanup *(Implementation Gap)*
**Priority:** High  
**Environment:** Either  
**Precondition:**  
- A temporary Goal exists with 2 milestones and 2 active reminders.
- *(Note: Frontend currently lacks a delete button in the UI; test executes via API or goalsStore)*.

**Actions:**
1. Send `DELETE /api/v1/goals/<GOAL_ID>`.
2. Inspect database for milestones and reminders.

**Expected output:**
- Goal is deleted (`HTTP 204 No Content`).
- Database cascade deletes all associated milestones (`milestones.goal_id` foreign key cascade).
- Associated reminders are cleaned up or set to null/cancelled without orphan errors.

**Verification:**
- **Network/API:** `DELETE /api/v1/goals/<GOAL_ID>` returns `HTTP 204 No Content`.
- **DB:** `SELECT count(*) FROM goals WHERE id = <GOAL_ID>;` equals 0; `SELECT count(*) FROM milestones WHERE goal_id = <GOAL_ID>;` equals 0.

**Cleanup:**
- None.

---

#### GOAL-UI-06 — Adjust with Mr. Bloom (Hybrid Handoff)
**Priority:** Core  
**Environment:** Either  
**Precondition:**  
- User has 1 active Goal with an existing roadmap.

**Actions:**
1. Navigate to `/goals`.
2. Select the Goal to view its details.
3. Click "ADJUST WITH MR. BLOOM".
4. In Mr. Bloom, observe the Roadmap Draft loaded.
5. Provide a structural edit prompt (e.g., "Add a new milestone for deployment").
6. Click Save in the draft preview.
7. Return to `/goals` and verify the Goal's roadmap updated.

**Expected output:**
- Handoff from Goal UI navigates to `/mr-bloom?goalId=<GOAL_ID>`.
- Chat context successfully loads the goal as a `RoadmapDraft`.
- Changes save back to the existing goal idempotently.

**Verification:**
- **UI:** Handoff correctly populates the chat context.
- **Network/API:** `GET /api/v1/goals/<GOAL_ID>/draft` loads the state.
- **DB:** `goals` and `milestones` tables reflect the updated structure.

---

### Group 9: Garden

#### GARDEN-01 — Default Starter Plant Auto-Provisioning
**Priority:** Core  
**Environment:** Either  
**Precondition:**  
- Newly registered and verified user account accesses garden for the first time.

**Actions:**
1. Navigate to `/today` or click `YOUR GARDEN` to open `/garden-selection`.
2. Inspect garden state and sidebar.

**Expected output:**
- User automatically receives free starter plant: Monstera Deliciosa (`species: "monstera"`, unlock cost `0`).
- `selected_plant_id` is set to the Monstera plant ID.
- Plant ownership record is created in `plant_ownerships`.
- Growth stage is `SPROUTING` (0 growth points).
- Vitality defaults to `100` (Healthy).
- Sidebar displays Monstera sprout sprite.

**Verification:**
- **UI:** Garden panel shows "UNLOCKED PLANTS 1 / 5"; Monstera marked "SELECTED".
- **Network/API:** `GET /api/v1/garden` returns `selected_plant_id` matching Monstera, `vitality: 100`, `growth_stage: "SPROUTING"`.
- **DB:** `SELECT count(*) FROM plant_ownerships WHERE user_id = <USER_ID>;` equals `1`.

**Cleanup:**
- Retain account for garden progression.

---

#### GARDEN-02 — Growth Stage Progression Independence from Vitality
**Priority:** Core  
**Environment:** Either  
**Precondition:**  
- User's garden has 0 growth points (`SPROUTING`).
- Growth thresholds: `SPROUTING` (0-99), `GROWING` (100-299), `BLOOMING` (300-699), `FLOURISHING` (700+).

**Actions:**
1. Complete 10 tasks to earn 100 growth points (or stage via DB `UPDATE garden_states SET growth_points = 100 WHERE user_id = <USER_ID>;`).
2. Refresh `/garden-selection`. Observe stage.
3. Advance growth points to 350 (`BLOOMING`). Observe stage.
4. Advance growth points to 750 (`FLOURISHING`). Observe stage.

**Expected output:**
- At 100 pts: `growth_stage` is `GROWING`. Plant sprite updates to young foliage.
- At 350 pts: `growth_stage` is `BLOOMING`. Plant sprite updates to mature flowering/bloom frame.
- At 750 pts: `growth_stage` is `FLOURISHING`. Plant sprite updates to full lush frame.
- Changing vitality down to 0 does NOT downgrade growth points or growth stage.

**Verification:**
- **UI:** Garden panel and widget display correct growth stage sprites.
- **Network/API:** `GET /api/v1/garden` returns correct `growth_stage` matching points.
- **DB:** `SELECT growth_points FROM garden_states WHERE user_id = <USER_ID>;` matches expected points.

**Cleanup:**
- Reset growth points to 0 if desired.

---

#### GARDEN-03 — Deterministic Vitality Lazy Decay
**Priority:** Core  
**Environment:** Either  
**Precondition:**  
- Plant was watered at timestamp `T0`. Vitality is 100.
- Decay formula: 10 vitality points per 24 hours elapsed.

**Actions:**
1. Simulate time passage of 3 days (72 hours) by updating `last_watered_at = NOW - INTERVAL '3 days'`.
2. Call `GET /api/v1/garden`.
3. Simulate time passage of 11 days (264 hours): `last_watered_at = NOW - INTERVAL '11 days'`.
4. Call `GET /api/v1/garden`.

**Expected output:**
- Step 2: Elapsed days = 3. Decay = 30. Vitality returns `70` (`THIRSTY` presentation tier, atlas frame 12).
- Step 4: Elapsed days = 11. Decay = 110. Vitality clamps at `0` (`DORMANT` presentation tier, atlas frame 15).
- Plant does NOT die permanently. All growth points and unlocks remain intact.

**Verification:**
- **UI:** Plant sprite reflects thirsty (frame 12) and dormant (frame 15) states without disappearance.
- **Network/API:** `GET /api/v1/garden` returns `vitality: 70`, then `vitality: 0`.
- **DB:** `garden_states.growth_points` and `plant_ownerships` remain untouched.

**Cleanup:**
- Retain state for watering test `GARDEN-04`.

---

#### GARDEN-04 — Plant Watering and Vitality Restoration *(Implementation Gap)*
**Priority:** Core  
**Environment:** Either  
**Precondition:**  
- User's plant has vitality = 0 (dormant).
- User has `water_balance >= 1`.
- *(Note: Frontend lacks a watering button; execute via `POST /api/v1/garden/water`)*.

**Actions:**
1. Call `POST /api/v1/garden/water`.
2. Inspect API response.
3. Refresh `/garden-selection` or widget.

**Expected output:**
- Water balance decrements by 1 (`WATERING_COST`).
- `last_watered_at` updates to current UTC timestamp.
- Vitality immediately restores to `100` (`HEALTHY`).
- Plant sprite returns from dormant (frame 15) to healthy growth frame.
- An event of type `WATER_PLANT` with amount `-1` is recorded in `reward_events`.

**Verification:**
- **UI:** Plant visually revives to healthy foliage; Water counter decrements by 1.
- **Network/API:** `POST /api/v1/garden/water` returns `{"water_balance": ..., "vitality": 100, "last_watered_at": "..."}`.
- **DB:** `SELECT water_balance, last_watered_at FROM garden_states WHERE user_id = <USER_ID>;` shows deducted water and current time.

**Cleanup:**
- None.

---

#### GARDEN-05 — Active Plant Switching and Permanent Unlocks
**Priority:** Core  
**Environment:** Either  
**Precondition:**  
- User owns both Monstera (unlocked) and Sunflower (unlocked).
- Currently active plant is Monstera.

**Actions:**
1. Open Garden Dialog (`/garden-selection`).
2. Navigate carousel to "Sunflower".
3. Click the `SELECT` button.
4. Observe UI.
5. Close dialog and inspect App Sidebar and Desktop Widget.

**Expected output:**
- Sunflower button changes from `SELECT` to disabled `SELECTED`.
- `selected_plant_id` updates to Sunflower in backend.
- Sidebar and Widget immediately switch plant rendering from Monstera to Sunflower sprite.
- Switching plants is completely free (costs 0 Water, 0 Leaves).
- Previous Monstera remains permanently unlocked.

**Verification:**
- **UI:** Sunflower displayed in sidebar and widget; carousel displays "SELECTED".
- **Network/API:** `POST /api/v1/garden/plants/<SUNFLOWER_ID>/select` returns `HTTP 200 OK` with `selected_plant_id: <SUNFLOWER_ID>`.
- **DB:** `SELECT selected_plant_id FROM garden_states WHERE user_id = <USER_ID>;` equals Sunflower ID.

**Cleanup:**
- Switch back to Monstera if desired.

---

### Group 10: Water Rewards

#### WATER-01 — Valid Completed Focus Effort Awards Water
**Priority:** Core  
**Environment:** Either  
**Precondition:**  
- User's initial `water_balance = 0`.
- An active focus run exists.

**Actions:**
1. Finish focus session with outcome `DONE`.
2. Check garden water balance.

**Expected output:**
- `water_balance` increments by 1 (`WATER_PER_POMODORO`).
- `reward_events` ledger records 1 row:
  - `event_type = 'FOCUS_COMPLETED'`
  - `resource_type = 'WATER'`
  - `amount = 1`
  - `idempotency_key = 'focus_completed_<RUN_ID>'`
  - `source_focus_run_id = <RUN_ID>`

**Verification:**
- **UI:** Sidebar water counter displays `1`.
- **Network/API:** `GET /api/v1/garden` returns `water_balance: 1`.
- **DB:** `SELECT water_balance FROM garden_states WHERE user_id = <USER_ID>;` equals `1`.

**Cleanup:**
- None.

---

#### WATER-02 — Skipped / Invalid Focus Session Yields Zero Water
**Priority:** High  
**Environment:** Either  
**Precondition:**  
- User's initial `water_balance = 1`.
- Active focus session exists.

**Actions:**
1. Finish focus session with outcome `SKIP`.
2. Check garden water balance.

**Expected output:**
- Water balance remains strictly `1` (no water awarded).
- No new row is inserted into `reward_events`.

**Verification:**
- **UI:** Water counter remains `1`.
- **Network/API:** `GET /api/v1/garden` returns `water_balance: 1`.
- **DB:** No `FOCUS_COMPLETED` record exists for this skipped run ID.

**Cleanup:**
- None.

---

#### WATER-03 — Idempotency on Repeated Finish Requests
**Priority:** Core  
**Environment:** Either  
**Precondition:**  
- A focus run has already been finished and awarded 1 Water.

**Actions:**
1. Send duplicate `POST /api/v1/focus/finish` with identical `run_id` and outcome `DONE`.
2. Check database and water balance.

**Expected output:**
- Server returns existing ended focus run (`HTTP 200 OK`).
- Water is NOT awarded a second time.
- Water balance remains unchanged.
- Unique constraint on `reward_events.idempotency_key` guarantees ledger idempotency.

**Verification:**
- **Network/API:** Response returns successfully without duplicating state.
- **DB:** Exactly 1 ledger row exists for `focus_completed_<RUN_ID>`.

**Cleanup:**
- None.

---

### Group 11: Leaf Rewards

#### LEAF-01 — Meaningful Task Completion Awards Leaves
**Priority:** Core  
**Environment:** Either  
**Precondition:**  
- User has `leaves_balance = 0`.
- Today plan has pending task `TASK A`.

**Actions:**
1. Complete `TASK A` (via focus outcome `DONE` or by setting status to `COMPLETED`).
2. Inspect sidebar counter and garden state.

**Expected output:**
- `leaves_balance` increments by 1 (`LEAVES_PER_TASK`).
- `growth_points` increments by 10 (`TASK_COMPLETION`).
- Ledger records `event_type = 'TASK_COMPLETED'`, `resource_type = 'LEAVES'`, `amount = 1`, `idempotency_key = 'task_completed_<TASK_ID>'`.

**Verification:**
- **UI:** Sidebar leaves counter shows `1`.
- **Network/API:** `GET /api/v1/garden` returns `leaves_balance: 1, growth_points: 10`.
- **DB:** `SELECT leaves_balance, growth_points FROM garden_states WHERE user_id = <USER_ID>;` shows `1` and `10`.

**Cleanup:**
- None.

---

#### LEAF-02 — Meaningful Milestone Completion Awards Leaves
**Priority:** Core  
**Environment:** Either  
**Precondition:**  
- User has milestone `MS 1` in `PENDING` status.
- Current `leaves_balance = 1`.

**Actions:**
1. On `/goals`, update `MS 1` status to `COMPLETED`.
2. Inspect sidebar counter.

**Expected output:**
- `leaves_balance` increments by 1 (`LEAVES_PER_MILESTONE`).
- `growth_points` increments by 50 (`MILESTONE_COMPLETION`).
- Ledger records `event_type = 'MILESTONE_COMPLETED'`, `idempotency_key = 'milestone_completed_<MS_ID>'`.

**Verification:**
- **UI:** Leaves counter shows `2`.
- **Network/API:** `GET /api/v1/garden` reflects new balance.
- **DB:** `reward_events` has row with `source_milestone_id = <MS_ID>`.

**Cleanup:**
- None.

---

#### LEAF-03 — Reward Farming Prevention via Idempotency Keys
**Priority:** Core  
**Environment:** Either  
**Precondition:**  
- `TASK A` was previously marked `COMPLETED` and awarded 1 Leaf.

**Actions:**
1. In Today UI or via API, toggle `TASK A` status back to `PENDING`.
2. Observe leaves balance (remains unchanged, does not award negative leaves).
3. Toggle `TASK A` status to `COMPLETED` a second time.
4. Inspect leaves balance.

**Expected output:**
- Second completion does NOT award a second Leaf.
- `leaves_balance` remains strictly at previous balance.
- Ledger insertion conflict on `task_completed_<TASK_ID>` returns `None` and skips award.

**Verification:**
- **UI:** Leaves counter does not increase on re-completion.
- **Network/API:** `PATCH /api/v1/today/tasks/<TASK_ID>/status` succeeds with `status: "COMPLETED"`.
- **DB:** `SELECT count(*) FROM reward_events WHERE idempotency_key = 'task_completed_<TASK_ID>';` strictly equals `1`.

**Cleanup:**
- None.

---

### Group 12: Plant Unlocks

#### PLANT-01 — Inspect Plant Catalog (5 Preset MVP Species)
**Priority:** Core  
**Environment:** Either  
**Precondition:**  
- User is logged in and opens Garden Selection Dialog (`/garden-selection`).

**Actions:**
1. Cycle through all plants using the next arrow `>`.
2. Inspect name, description, cost, and unlock status for all 5 plants.

**Expected output:**
- Exactly 5 species are present:
  1. **Monstera Deliciosa:** Cost `0`, `is_unlocked: true`
  2. **Sunflower:** Cost `10` Leaves, `is_unlocked: false`
  3. **Bonsai Tree:** Cost `20` Leaves, `is_unlocked: false`
  4. **Jasmine:** Cost `15` Leaves, `is_unlocked: false`
  5. **Lavender:** Cost `15` Leaves, `is_unlocked: false`
- Locked plants show lock icon and required cost.

**Verification:**
- **UI:** All 5 plants cycle with correct names, descriptions, and costs.
- **Network/API:** `GET /api/v1/garden` catalog array contains 5 items matching `99_seed.sql`.

**Cleanup:**
- None.

---

#### PLANT-02 — Rejection of Plant Unlock with Insufficient Leaves
**Priority:** High  
**Environment:** Either  
**Precondition:**  
- User has `leaves_balance = 2`.
- Sunflower requires `10` leaves.

**Actions:**
1. Navigate to Sunflower in Garden Selection Dialog.
2. Observe Action Panel.
3. Attempt to click `UNLOCK` (or send `POST /api/v1/garden/plants/<SUNFLOWER_ID>/unlock`).

**Expected output:**
- `UNLOCK` button is disabled in UI.
- Text displays: "Need 8 more leaves to unlock".
- Direct API invocation returns `HTTP 409 Conflict` with `detail.code: "INSUFFICIENT_LEAVES"`.
- Balance is NOT deducted.

**Verification:**
- **UI:** Disabled unlock button; missing leaves helper text visible.
- **Network/API:** Returns `HTTP 409 Conflict` with `required: 10, available: 2`.
- **DB:** No ownership row inserted.

**Cleanup:**
- None.

---

#### PLANT-03 — Successful Plant Unlock with Leaf Deduction
**Priority:** Core  
**Environment:** Either  
**Precondition:**  
- User has `leaves_balance = 12` (earned or staged in DB).
- Sunflower is locked (`unlock_cost = 10`).

**Actions:**
1. Open Garden Selection Dialog and navigate to Sunflower.
2. Verify `UNLOCK` button is enabled.
3. Click `UNLOCK`.

**Expected output:**
- Sunflower unlocks immediately.
- `leaves_balance` decrements by 10 (from 12 to 2).
- Action panel changes from `UNLOCK` to `SELECT`.
- Unlocked count updates to `2 / 5`.
- Ledger records `PLANT_UNLOCK` with amount `-10`.

**Verification:**
- **UI:** Unlock button changes to `SELECT`; Leaves counter shows `2`.
- **Network/API:** `POST /api/v1/garden/plants/<SUNFLOWER_ID>/unlock` returns `HTTP 200 OK` with updated catalog where Sunflower `is_unlocked: true`.
- **DB:** `SELECT * FROM plant_ownerships WHERE plant_id = <SUNFLOWER_ID> AND user_id = <USER_ID>;` returns 1 row.

**Cleanup:**
- Keep Sunflower unlocked for `PLANT-04`.

---

#### PLANT-04 — Permanent Plant Ownership and Duplicate Unlock Idempotency
**Priority:** Core  
**Environment:** Either  
**Precondition:**  
- User has unlocked Sunflower.

**Actions:**
1. Close and reload application (`F5` or restart desktop).
2. Open Garden Selection Dialog.
3. Verify Sunflower remains unlocked.
4. Send direct API call: `POST /api/v1/garden/plants/<SUNFLOWER_ID>/unlock`.

**Expected output:**
- Sunflower remains permanently unlocked after reload.
- Duplicate unlock API call is idempotent: returns `HTTP 200 OK` without deducting any additional leaves.
- Leaves balance remains unchanged.

**Verification:**
- **UI:** Sunflower is unlocked immediately upon loading.
- **Network/API:** Duplicate unlock request succeeds without deducting currency.
- **DB:** Exactly 1 `PlantOwnership` row exists for Sunflower.

**Cleanup:**
- None.

---

### Group 13: Ambient Environment

#### SEASON-01 — Four Seasonal Visual Presentation Contexts
**Priority:** Core  
**Environment:** Either  
**Precondition:**  
- User is on `/settings`.
- Widget or Today page garden panel is visible.

**Actions:**
1. Set "Garden Season Override" to `SPRING`. Save and inspect vegetation.
2. Set "Garden Season Override" to `SUMMER`. Save and inspect vegetation.
3. Set "Garden Season Override" to `AUTUMN`. Save and inspect vegetation.
4. Set "Garden Season Override" to `WINTER`. Save and inspect vegetation.

**Expected output:**
- Spring: Fresh green vegetation layer (`spring.png`).
- Summer: Lush vibrant foliage layer (`summer.png`).
- Autumn: Golden/orange seasonal layer (`autumn.png`).
- Winter: Snow-dusted vegetation layer (`winter.png`).
- Changing season affects ONLY visual decoration; it does NOT alter scheduler, water, leaves, or timers.

**Verification:**
- **UI:** Layer asset swaps dynamically matching selected season.
- **Network/API:** `PUT /api/v1/me/settings` updates `scene_season`.

**Cleanup:**
- Reset season to `AUTO`.

---

#### TIME-01 — Six Diurnal Sky and Lighting Transitions
**Priority:** Core  
**Environment:** Either  
**Precondition:**  
- Open `/widget-preview` or adjust local client clock across the 6 diurnal brackets:
  - `DAWN`: 05:00 - 06:59
  - `MORNING`: 07:00 - 10:59
  - `NOON`: 11:00 - 13:59
  - `AFTERNOON`: 14:00 - 16:59
  - `SUNSET`: 17:00 - 19:59
  - `NIGHT`: 20:00 - 04:59

**Actions:**
1. Open `/widget-preview?shot=1&time=06` (Dawn).
2. Open `/widget-preview?shot=1&time=09` (Morning).
3. Open `/widget-preview?shot=1&time=12` (Noon).
4. Open `/widget-preview?shot=1&time=15` (Afternoon).
5. Open `/widget-preview?shot=1&time=18` (Sunset).
6. Open `/widget-preview?shot=1&time=22` (Night).

**Expected output:**
- Sky background texture matches time slot:
  - Dawn: Soft early morning pastel sky (`dawn.png`).
  - Morning: Bright blue morning sky (`morning.png`).
  - Noon: Vivid midday sunlight (`noon.png`).
  - Afternoon: Mellow daytime light (`afternoon.png`).
  - Sunset: Orange/crimson twilight sky (`sunset.png`).
  - Night: Dark starry night with illuminated skyline (`night.png`).

**Verification:**
- **UI:** Background sky asset correctly corresponds to hour parameter.

**Cleanup:**
- None.

---

#### WEATHER-01 — Five Weather Atmospheric Ambiances
**Priority:** Core  
**Environment:** Either  
**Precondition:**  
- Open `/widget-preview` with weather override parameter.

**Actions:**
1. View `/widget-preview?weather=CLEAR`.
2. View `/widget-preview?weather=CLOUDY`.
3. View `/widget-preview?weather=OVERCAST`.
4. View `/widget-preview?weather=RAIN`.
5. View `/widget-preview?weather=THUNDERSTORM`.

**Expected output:**
- `CLEAR`: Clean sky, zero cloud or weather overlays.
- `CLOUDY`: Static fluffy white cloud layer (`cloudy.png`).
- `OVERCAST`: Dense gray cloud cover layer (`overcast.png`).
- `RAIN`: Overcast cloud cover + animated rain streaks.
- `THUNDERSTORM`: Dark storm tint overlay (`storm-overlay.png`) + high-density rain streaks.

**Verification:**
- **UI:** Weather layers render accurately according to specification.

**Cleanup:**
- None.

---

#### WEATHER-02 — Continuous Rain Animation Layer Verification
**Priority:** High  
**Environment:** Either  
**Precondition:**  
- Widget is rendering `RAIN` or `THUNDERSTORM`.

**Actions:**
1. Observe rain animation for 10 seconds.
2. In Settings, toggle "Animate rain in widget" to OFF.
3. Save and observe widget.

**Expected output:**
- In `RAIN`: Canvas renders ~30 continuous falling pixel rain streaks (600-1000ms duration).
- In `THUNDERSTORM`: Denser rain streaks (~60 streaks, 400-700ms duration).
- When toggled OFF: Rain animation stops or hides canvas layer while retaining static storm background.

**Verification:**
- **UI:** HTML5 canvas `<canvas>` or `RainLayer` renders animated streaks; pauses/stops when disabled.

**Cleanup:**
- Re-enable rain animation.

---

#### AMBIENT-01 — Critical Invariant: Zero Productivity or Reward Side Effects
**Priority:** Core  
**Environment:** Either  
**Precondition:**  
- Weather is set to `RAIN` or `THUNDERSTORM`.
- Plant has 0 Water and 50 Vitality.

**Actions:**
1. Leave the app running in heavy rain for 5 minutes.
2. Check `water_balance`.
3. Check `plant vitality`.
4. Check task scheduler durations.

**Expected output:**
- Heavy rain does NOT grant Water to the user balance.
- Heavy rain does NOT water or heal the plant vitality.
- Weather does NOT alter focus session durations or task deadlines.
- Productivity and economy logic remain 100% deterministic and unaffected by ambient weather.

**Verification:**
- **DB:** `water_balance` remains identical; no free resource events in `reward_events`.

**Cleanup:**
- None.

---

### Group 14: Statistics

#### STATS-01 — Summary Metrics Calculation
**Priority:** Core  
**Environment:** Either  
**Precondition:**  
- User has logged focus runs and completed daily plans over the past week:
  - Total completed focus runs: 4 runs of 30 min each (2.0 total study hours).
  - Completed on 2 distinct calendar days.
  - 1 completed plan, 1 unfinished plan.

**Actions:**
1. Navigate to `/statistics`.
2. Inspect the top "Summary Metrics" card row.

**Expected output:**
- Summary cards display:
  - "TOTAL STUDY TIME": `2 hrs 0 mins`
  - "STUDY DAYS": `2`
  - "COMPLETED PLANS": `1`
  - "UNFINISHED PLANS": `1`
- No invented or uncalculated metrics appear.

**Verification:**
- **UI:** Numbers in cards match actual database records.
- **Network/API:** `GET /api/v1/statistics/summary?start_date=...&end_date=...` returns `HTTP 200 OK` with JSON fields matching UI cards.
- **DB:** Aggregation queries on `focus_runs` and `daily_plans` corroborate values.

**Cleanup:**
- None.

---

#### STATS-02 — Date Range Switching (Current Week, Last Week, Current Month)
**Priority:** High  
**Environment:** Either  
**Precondition:**  
- User is on `/statistics`.

**Actions:**
1. In the header dropdown / pill selector, click "Last Week".
2. Observe metrics, chart, and calendar update.
3. Click "Current Month".
4. Observe metrics update.
5. Click "Current Week".

**Expected output:**
- Selecting each range issues new requests for `summary` and `daily` metrics bounded by the selected start and end dates.
- UI updates without error banners.
- Calendar highlights studied days falling strictly within the selected date window.

**Verification:**
- **UI:** Chart subtitle updates (e.g., "Current Month"); cards re-render.
- **Network/API:** `GET /api/v1/statistics/summary` and `/daily` called with respective date bounds.

**Cleanup:**
- Reset to "Current Week".

---

#### STATS-03 — Daily Study Time Chart and Calendar Days
**Priority:** Normal  
**Environment:** Either  
**Precondition:**  
- User studied 2.5 hours on Wednesday and 1.0 hour on Friday.

**Actions:**
1. On `/statistics`, inspect the "Daily Study Time" bar chart.
2. Inspect the "Study Calendar" panel.

**Expected output:**
- Bar chart displays bars corresponding to Wednesday (2.5h) and Friday (1.0h); other days are 0h.
- Calendar displays dots/badges on Wednesday and Friday dates (`status: "studied"`).
- Days with 0 study hours show no studied indicator.

**Verification:**
- **UI:** Chart bar heights proportional to hours; calendar dots positioned on exact day numbers.
- **Network/API:** `GET /api/v1/statistics/daily` array has entries with `hours > 0` for Wednesday and Friday.

**Cleanup:**
- None.

---

#### STATS-04 — Plan History Filtering and Pagination
**Priority:** High  
**Environment:** Either  
**Precondition:**  
- User has 6 historical daily plans across the selected range (4 completed, 2 unfinished).

**Actions:**
1. In the "Plan History" panel, observe page 1 (items per page: 4).
2. Click page `2` in pagination controls.
3. Change filter from "All" to "Completed".
4. Change filter to "Unfinished".

**Expected output:**
- Page 1 shows 4 items; page 2 shows remaining 2 items.
- "Completed" filter shows only plans with completed status badge.
- "Unfinished" filter shows only plans with unfinished status badge.
- Each item displays plan date, plan name, and completed/total task fraction (e.g., `3/3 tasks`).

**Verification:**
- **UI:** Correctly filtered items and page numbers rendered.
- **Network/API:** `GET /api/v1/statistics/plan-history?status=Completed&page=1&page_size=4` returns `total_items: 4, total_pages: 1`.

**Cleanup:**
- None.

---

### Group 15: Tauri / Desktop Lifecycle

#### DESKTOP-01 — Dual-Window Startup Lifecycle (Main Hidden, Widget Visible)
**Priority:** Core  
**Environment:** Tauri Desktop Only  
**Precondition:**  
- Blooming desktop application is launched freshly from executable or terminal.

**Actions:**
1. Launch `Blooming.exe`.
2. Observe desktop display.
3. Check system tray.

**Expected output:**
- Companion Widget window appears automatically on desktop at `/widget`.
- Main application window starts HIDDEN (`visible: false` in `tauri.conf.json`) to prevent intrusive popups on startup.
- Blooming system tray icon is initialized in the Windows notification area.

**Verification:**
- **UI:** Widget visible on desktop; main app hidden; tray icon present.
- **Desktop API:** `Window.getByLabel("companion-widget").isVisible()` is `true`; `Window.getByLabel("main").isVisible()` is `false`.

**Cleanup:**
- None.

---

#### DESKTOP-02 — System Tray Context Menu Interactions
**Priority:** Core  
**Environment:** Tauri Desktop Only  
**Precondition:**  
- App is running in system tray. Both windows are hidden or minimized.

**Actions:**
1. Left-click the Blooming tray icon.
2. Minimize the main window.
3. Right-click the Blooming tray icon to open the context menu.
4. Inspect menu items:
   - "Open Blooming"
   - "Show companion"
   - "Quit"
5. Click "Show companion".
6. Right-click tray and click "Quit".

**Expected output:**
- Step 1: Left-click opens, unminimizes, and focuses the main application window.
- Step 4-5: "Show companion" restores and focuses the desktop widget window.
- Step 6: "Quit" exits the entire desktop application cleanly (process terminates).

**Verification:**
- **UI:** Menus trigger expected window visibility; Quit closes all processes.
- **System:** Blooming process vanishes from Task Manager upon clicking Quit.

**Cleanup:**
- Relaunch application for subsequent tests.

---

#### DESKTOP-03 — Cross-Window Event Synchronization via Tauri IPC
**Priority:** Core  
**Environment:** Tauri Desktop Only  
**Precondition:**  
- Both Main Window (`main`) and Widget Window (`companion-widget`) are open side-by-side.

**Actions:**
1. In the Main Window on `/today`, start a focus session on an upcoming task.
2. In the Main Window on `/garden-selection`, switch the active plant to Sunflower.
3. In the Main Window on `/settings`, change Mr. Bloom's name or season override.

**Expected output:**
- Action 1: Main window emits `blooming:schedule-updated`. Widget instantly switches from idle to `focusing` countdown without delay.
- Action 2: Widget updates active plant sprite to Sunflower without requiring widget reload.
- Action 3: Main window emits `blooming:settings-updated`. Widget updates character/environment.

**Verification:**
- **UI:** Instant cross-window updates observed visually in real time.
- **Network/API:** IPC events received via Tauri `listen()` listeners.

**Cleanup:**
- None.

---

#### DESKTOP-04 — Reminder Background Ownership Longevity
**Priority:** Core  
**Environment:** Tauri Desktop Only  
**Precondition:**  
- Desktop app is running. Main window is closed (`X`).
- Widget is the designated reminder owner (`desktop.isReminderOwner()` returns `true`).

**Actions:**
1. Close the main window (hides to tray).
2. Trigger a due reminder on the backend (e.g. advance milestone due date).
3. Wait up to 60 seconds (polling interval).

**Expected output:**
- Root layout polling on the widget window continues firing in the background.
- Tray icon detects the due reminder and turns on the red alert dot (`set_tray_icon(alert: true)`).
- Hiding windows did NOT kill the background reminder timer.

**Verification:**
- **UI:** Tray alert icon turns red while main window remains hidden.
- **Log:** Console shows periodic background reminder polling ticks.

**Cleanup:**
- Clear reminder to reset tray icon.

---

### Group 16: Failure / Offline

#### FAILURE-APP-01 — Backend API Unreachable Graceful Handling
**Priority:** High  
**Environment:** Either  
**Precondition:**  
- Stop the backend server process.

**Actions:**
1. With backend stopped, navigate to `/today`.
2. Observe error presentation.
3. Navigate to `/statistics`.
4. Observe error presentation.

**Expected output:**
- Application does NOT crash with a blank white screen.
- Today page displays a graceful load error: "Failed to load today plan."
- Statistics page displays a styled error banner: "Failed to load statistics" with a "Retry" button.
- User interface remains responsive.

**Verification:**
- **UI:** Graceful error messages and retry buttons visible.
- **Network/API:** Network requests fail with `ERR_CONNECTION_REFUSED`.

**Cleanup:**
- Restart backend server.

---

#### FAILURE-APP-02 — External Weather Provider Failure Fallback
**Priority:** High  
**Environment:** Either  
**Precondition:**  
- Open-Meteo weather API is unreachable or simulated network failure for `api.open-meteo.com`.

**Actions:**
1. Call `GET /api/v1/weather/current`.
2. Inspect response and widget presentation.

**Expected output:**
- Weather service catches provider failure.
- Returns last known cached weather if available (`status: "STALE"`), or falls back to clear sky (`status: "UNAVAILABLE"`).
- API does NOT throw an unhandled 500 error.
- Widget renders clean fallback sky without crashing.

**Verification:**
- **UI:** Fallback clear sky or stale weather rendered.
- **Network/API:** `GET /api/v1/weather/current` returns `HTTP 200 OK` with `status: "UNAVAILABLE", condition: "CLEAR"`.

**Cleanup:**
- None.

---

#### FAILURE-APP-03 — Focus Session Finish Network Retry Resilience
**Priority:** High  
**Environment:** Tauri Desktop  
**Precondition:**  
- Focus session is in `ending` state on the widget.

**Actions:**
1. Temporarily pause backend network connection.
2. In widget, click `DONE`.
3. Observe error alert.
4. Restore backend network connection.
5. In widget, click `DONE` again.

**Expected output:**
- Step 2-3: Widget displays inline error banner: "Error: Failed to complete session. Try again.". Outcome buttons remain visible and clickable.
- Step 4-5: Second attempt succeeds, records `DONE`, awards resources, and closes ending state without duplicating data.

**Verification:**
- **UI:** Error message shown on failure; clears on successful retry.
- **DB:** Exactly one ended session and one set of reward events saved.

**Cleanup:**
- None.

---

#### FAILURE-APP-04 — Transaction Atomicity Rollback on Save Failure
**Priority:** Core  
**Environment:** Either  
**Precondition:**  
- Test user has active plan.

**Actions:**
1. Trigger a complex multi-entity update (e.g. focus finish with re-plan and reward allocation) where database encounters an integrity violation or simulated database interruption.

**Expected output:**
- FastAPI dependency `get_db_session` triggers `await session.rollback()`.
- No partial state is committed (e.g., Water is not awarded if task status update fails; plan blocks are not partially updated).
- Database remains 100% consistent with pre-request state.

**Verification:**
- **DB:** Verify all related tables (`reward_events`, `focus_runs`, `tasks`, `plan_blocks`) retain exact consistent prior state.

**Cleanup:**
- None.

---

### Group 17: Security & User Isolation

#### SECURITY-APP-01 — Cross-User Plan and Task Access Prohibition
**Priority:** Core  
**Environment:** Either  
**Precondition:**  
- `User A` owns Daily Plan `PLAN_A` and Task `TASK_A`.
- `User B` is authenticated with valid JWT token `TOKEN_B`.

**Actions:**
1. Using `TOKEN_B`, attempt to get `TASK_A`: `GET /api/v1/planning/tasks/<TASK_A_ID>`.
2. Using `TOKEN_B`, attempt to edit `TASK_A`: `PATCH /api/v1/today/tasks/<TASK_A_ID>` with new title.
3. Using `TOKEN_B`, attempt to update status: `PATCH /api/v1/today/tasks/<TASK_A_ID>/status`.

**Expected output:**
- All requests are rejected with `HTTP 404 Not Found` (ResourceNotFoundError) or `HTTP 403 Forbidden` (UnauthorizedOwnershipError).
- `User B` cannot read, modify, or complete tasks owned by `User A`.
- `TASK_A` remains untouched.

**Verification:**
- **Network/API:** Returns `HTTP 404` or `HTTP 403`.
- **DB:** `SELECT title, status FROM tasks WHERE id = <TASK_A_ID>;` remains unchanged.

**Cleanup:**
- None.

---

#### SECURITY-APP-02 — Cross-User Goal and Milestone Isolation
**Priority:** Core  
**Environment:** Either  
**Precondition:**  
- `User A` owns Goal `GOAL_A` and Milestone `MS_A`.
- `User B` is authenticated with `TOKEN_B`.

**Actions:**
1. Using `TOKEN_B`, attempt `GET /api/v1/goals/<GOAL_A_ID>`.
2. Using `TOKEN_B`, attempt `PUT /api/v1/goals/<GOAL_A_ID>` with `{"title": "Hacked"}`.
3. Using `TOKEN_B`, attempt `PUT /api/v1/goals/<GOAL_A_ID>/milestones/<MS_A_ID>` with `{"status": "COMPLETED"}`.

**Expected output:**
- Requests return `HTTP 404 Not Found` or `HTTP 403 Forbidden`.
- `User B` cannot award themselves Leaves by completing `User A`'s milestones.
- No reward events are generated for `User B`.

**Verification:**
- **Network/API:** Responses strictly reject cross-tenant operations.
- **DB:** `SELECT * FROM goals WHERE id = <GOAL_A_ID>;` confirms title is not altered.

**Cleanup:**
- None.

---

#### SECURITY-APP-03 — Cross-User Focus Run and Reminder Action Prohibition
**Priority:** Core  
**Environment:** Either  
**Precondition:**  
- `User A` has active Focus Run `RUN_A` and due Reminder `REMINDER_A`.
- `User B` is authenticated with `TOKEN_B`.

**Actions:**
1. Using `TOKEN_B`, attempt `POST /api/v1/focus/finish` with `{"run_id": "<RUN_A_ID>", "outcome": "DONE"}`.
2. Using `TOKEN_B`, attempt `POST /api/v1/reminders/<REMINDER_A_ID>/actions` with `{"action_type": "MARK_COMPLETED"}`.

**Expected output:**
- Step 1: Rejected with `HTTP 404 Not Found` ("No active focus session to finish"). `User B` cannot manipulate `User A`'s focus session.
- Step 2: Rejected with `HTTP 404 Not Found` or `HTTP 403 Forbidden`.
- `User A`'s reminder remains intact.

**Verification:**
- **Network/API:** Both endpoints return `HTTP 404` / `403`.
- **DB:** `focus_runs` and `reminders` for `User A` remain in their active/due states.

**Cleanup:**
- None.

---

## 3. Coverage Matrix

| Feature / Domain | MVP Requirement | Repo Evidence (Source Files) | Manual Test Cases | Status |
|---|---|---|---|---|
| **User & Account** | Register, Login, Logout, JWT auth, verification tokens | `routes/auth.py`, `auth_service.py`, `authStore.ts`, `verify-email/+page.svelte` | `AUTH-01`, `AUTH-02`, `AUTH-03`, `AUTH-04`, `AUTH-05`, `AUTH-06` | **Covered** |
| **Onboarding & Settings** | Timezone, focus/break defaults, Bloom name, autostart, always-on-top | `routes/user_settings.py`, `SettingsState.svelte.ts`, `GeneralPanel.svelte`, `onboarding/+page.svelte` | `ONBOARD-01`, `SETTINGS-01`, `SETTINGS-02`, `SETTINGS-04`, `SETTINGS-05`, `SETTINGS-06` | **Covered** |
| **Quiet Hours** | Quiet hours suppression of reminders | `models/users.py`, `reminders_service.py` | `SETTINGS-03`, `REMINDER-01` | **Implementation Gap** *(Backend only; missing UI controls)* |
| **Saved Plan UI** | Saved plan display, task cards, breaks, geometry, date navigation | `routes/today.py`, `today/+page.svelte`, `TodayTimeline.svelte`, `timeline.ts` | `TODAY-UI-01`, `TODAY-UI-02`, `TODAY-UI-03`, `TODAY-UI-04`, `TODAY-UI-05` | **Covered** |
| **Pomodoro & Focus** | 25/5, 50/10, Custom, start, pause, resume, finish, single active session | `routes/focus.py`, `focus_service.py`, `widget/+page.svelte`, `RightRail.svelte` | `FOCUS-01`, `FOCUS-02`, `FOCUS-03`, `FOCUS-04`, `FOCUS-05`, `FOCUS-06` | **Covered** |
| **Re-planning** | Outcomes (DONE, EARLY, NEED_MORE_TIME, SKIP), preserve history, reschedule flexible | `today_service.py`, `focus_service.py`, `PlanRevision` model | `REPLAN-01`, `REPLAN-02`, `REPLAN-03`, `REPLAN-04`, `REPLAN-05` | **Covered** |
| **Desktop Widget** | DEFAULT, FOCUSING, SESSION_RESULT, window lifecycle, no chat/LLM | `src-tauri/src/lib.rs`, `desktopWindow.ts`, `widget/+page.svelte`, `CompanionWidget.svelte` | `WIDGET-01`, `WIDGET-02`, `WIDGET-03`, `WIDGET-05`, `WIDGET-06` | **Covered** |
| **Widget Reminders** | Reminders rendered inside widget speech bubble / panel | `ReminderPanel.svelte`, `widget-preview/+page.svelte` | `WIDGET-04` | **Implementation Gap** *(Widget preview only; missing live binding in widget page)* |
| **Reminders** | Milestone reminders, tray red dot, CREATE_PLAN, MARK_COMPLETED, MOVE, SNOOZE | `reminders_service.py`, `DueRemindersPanel.svelte`, `+layout.svelte` tray alert | `REMINDER-01`, `REMINDER-02`, `REMINDER-03`, `REMINDER-04`, `REMINDER-05` | **Covered** |
| **Persisted Goals** | Goal list, detail, roadmap sequence, milestone toggle, title edit | `routes/goals.py`, `goals_service.py`, `goals/+page.svelte`, `goalsStore.ts` | `GOAL-UI-01`, `GOAL-UI-02`, `GOAL-UI-03`, `GOAL-UI-04`, `GOAL-UI-05` | **Covered** |
| **Garden State & Plants** | Starter plant, 5 preset species, growth stages, plant switching | `garden_service.py`, `database/99_seed.sql`, `GardenPanel.svelte`, `state.svelte.ts` | `GARDEN-01`, `GARDEN-02`, `GARDEN-05`, `PLANT-01`, `PLANT-04`, `PLANT-05` | **Covered** |
| **Garden Watering** | Spend Water to restore plant vitality | `routes/garden.py` (`POST /garden/water`), `economy.py` | `GARDEN-04` | **Implementation Gap** *(Backend API only; missing UI watering button)* |
| **Vitality & Longevity** | Lazy decay over time, no permanent plant death | `economy.py` (`calculate_vitality`), `spriteMapper.ts` | `GARDEN-03` | **Covered** |
| **Water Rewards** | 1 Water per valid focus, 0 for skip, idempotency | `focus_service.py`, `economy.py`, `reward_events` ledger | `WATER-01`, `WATER-02`, `WATER-03` | **Covered** |
| **Leaf Rewards** | 1 Leaf per task/milestone, farming prevention via unique keys | `today_service.py`, `goals_service.py`, `reward_events` ledger | `LEAF-01`, `LEAF-02`, `LEAF-03` | **Covered** |
| **Plant Unlocks** | Deduct leaves, permanent unlock, insufficient leaves rejection | `garden_service.py`, `ActionPanel.svelte`, `state.svelte.ts` | `PLANT-02`, `PLANT-03`, `PLANT-04` | **Covered** |
| **Ambient Environment** | 4 seasons, 6 times of day, 5 weathers, animated rain, zero side-effects | `environment.ts`, `WidgetSceneBackground.svelte`, `RainLayer.svelte`, `weather_service.py` | `SEASON-01`, `TIME-01`, `WEATHER-01`, `WEATHER-02`, `AMBIENT-01` | **Covered** |
| **Statistics** | Study time, study days, plan history, calendar dots, date filters | `routes/statistics.py`, `statistics_service.py`, `statistics/+page.svelte` | `STATS-01`, `STATS-02`, `STATS-03`, `STATS-04` | **Covered** |
| **Desktop Lifecycle** | Tray menu, hide-on-close, IPC sync, timer continuity | `src-tauri/src/lib.rs`, `desktopWindow.ts`, `tauri.conf.json` | `DESKTOP-01`, `DESKTOP-02`, `DESKTOP-03`, `DESKTOP-04` | **Covered** |
| **Failure & Offline** | Backend down, weather fallback, transaction rollbacks | `api.ts`, `weather_service.py`, `deps.py` | `FAILURE-APP-01`, `FAILURE-APP-02`, `FAILURE-APP-03`, `FAILURE-APP-04` | **Covered** |
| **Security & Isolation** | Cross-tenant rejection for plans, tasks, goals, runs, reminders | `planning_service.py`, `goals_service.py`, `reminders_service.py`, `deps.py` | `SECURITY-APP-01`, `SECURITY-APP-02`, `SECURITY-APP-03` | **Covered** |
| **Outside MVP Items** | OS toast notifications, email milestone alerts, free-form widget chat | N/A | Excluded | **Outside MVP** |

---

## 4. Known Implementation Gaps

The following discrepancies between the MVP product specification and repository implementation were identified through code audit:

### GAP-01: Missing Frontend Control for Plant Watering
- **Feature:** Garden / Vitality System
- **MVP Expectation:** User spends earned Water to water their active plant, restoring vitality from thirsty/wilting/dormant to healthy.
- **Current Implementation:** Backend route `POST /garden/water` and service logic in `garden_service.py` are fully implemented, deducting 1 Water, recording `WATER_PLANT` in `reward_events`, and resetting `last_watered_at`. However, frontend components (`GardenPanel.svelte`, `GardenSelectionDialog.svelte`, `ActionPanel.svelte`) contain NO button, slider, or interaction to trigger plant watering. Water is only displayed as a passive numerical counter in `AppSidebar.svelte`.
- **Relevant Source Files:**
  - `backend/app/api/routes/garden.py` (Lines 33–38)
  - `backend/app/services/garden_service.py` (Lines 222–251)
  - `frontend/src/lib/features/garden-selection/components/organisms/ActionPanel.svelte`
- **Affected Manual Tests:** `GARDEN-04` (requires API/DevTools execution to trigger watering).

### GAP-02: Missing Frontend Configuration for Quiet Hours
- **Feature:** User Settings & Notifications
- **MVP Expectation:** User can configure quiet hours in Settings to suppress reminders during rest periods.
- **Current Implementation:** Database model `user_settings` (`quiet_hours_enabled`, `quiet_hours_start`, `quiet_hours_end`) and backend `reminders_service.py` (`get_due_reminders`) fully enforce quiet hours filtering. However, frontend `NotificationsPanel.svelte` only displays "Milestone reminder" lead time dropdown and "Email reminders" toggle, with no input fields for quiet hours.
- **Relevant Source Files:**
  - `backend/app/db/models/users.py` (Lines 178–182)
  - `backend/app/services/reminders_service.py` (Lines 103–106)
  - `frontend/src/lib/features/settings/components/organisms/NotificationsPanel.svelte`
- **Affected Manual Tests:** `SETTINGS-03` (must configure quiet hours via `PUT /me/settings` directly).

### GAP-03: Widget Missing Due Reminders Live Integration
- **Feature:** Desktop Widget Reminder Presentation
- **MVP Expectation:** Due reminders appear visually through Mr. Bloom / widget UI bubbles on the desktop.
- **Current Implementation:** Tauri root layout (`routes/+layout.svelte`) polls `/reminders/due` and activates the system tray alert red dot. In the main window, reminders appear on the Goals page (`DueRemindersPanel.svelte`). The widget component `ReminderPanel.svelte` exists and works in `/widget-preview?kind=reminders`, but production `routes/widget/+page.svelte` does not fetch due reminders or toggle presentation to `kind: "reminders"`.
- **Relevant Source Files:**
  - `frontend/src/routes/widget/+page.svelte` (Lines 220–265)
  - `frontend/src/lib/features/companion-widget/components/molecules/ReminderPanel.svelte`
  - `frontend/src/routes/+layout.svelte` (Lines 30–32)
- **Affected Manual Tests:** `WIDGET-04`, `REMINDER-01`.

### GAP-04: Email Reminders Toggle Non-Persisted
- **Feature:** Notifications Settings
- **MVP Expectation:** Email notifications are outside MVP scope, but the settings panel provides an "Email reminders" toggle.
- **Current Implementation:** The toggle in `NotificationsPanel.svelte` only persists to browser `localStorage` (`emailReminders`). The backend schema `UserSettingsUpdate` and database table `user_settings` have no `email_reminders` column and ignore this field.
- **Relevant Source Files:**
  - `frontend/src/lib/features/settings/model/SettingsState.svelte.ts` (Lines 66–72)
  - `backend/app/schemas/user_settings.py`

### GAP-05: Missing In-UI Goal and Milestone Deletion Controls
- **Feature:** Persisted Goals & Milestones
- **MVP Expectation:** User can manage and delete completed/stale goals and milestones.
- **Current Implementation:** Backend provides `DELETE /api/v1/goals/{goal_id}` and `DELETE /api/v1/goals/{goal_id}/milestones/{milestone_id}`. Frontend `goalsStore.ts` provides `deleteGoal()` and `deleteMilestone()`. However, `MyGoalsPanel.svelte` and `GoalDetailsPanel.svelte` provide no delete buttons in the UI.
- **Relevant Source Files:**
  - `frontend/src/lib/features/goals/stores/goalsStore.ts` (Lines 75–88)
  - `frontend/src/lib/features/goals/components/organisms/MyGoalsPanel.svelte`
- **Affected Manual Tests:** `GOAL-UI-05`.

---

## 5. Recommended Execution Order

Execute test scenarios in ten structured blocks to optimize setup, minimize state contamination, and maintain natural data flow:

```
Block 1: Auth & Account (AUTH-01 → AUTH-06)
  ↓
Block 2: Onboarding & Settings (ONBOARD-01 → SETTINGS-06)
  ↓
Block 3: Saved Plan UI (TODAY-UI-01 → TODAY-UI-05)
  ↓
Block 4: Pomodoro & Focus Execution (FOCUS-01 → FOCUS-06)
  ↓
Block 5: Replanning & Outcome Handling (REPLAN-01 → REPLAN-05)
  ↓
Block 6: Rewards & Garden Systems (WATER-01 → LEAF-03, GARDEN-01 → PLANT-05)
  ↓
Block 7: Goals & Milestone Reminders (GOAL-UI-01 → REMINDER-05)
  ↓
Block 8: Ambient Environment & Weather (SEASON-01 → AMBIENT-01)
  ↓
Block 9: Desktop Widget & Tauri Lifecycle (WIDGET-01 → DESKTOP-04)
  ↓
Block 10: Statistics, Failure & Security (STATS-01 → SECURITY-03)
```

### Block 1 — Authentication & Account
- **Cases:** `AUTH-01`, `AUTH-02`, `AUTH-03`, `AUTH-04`, `AUTH-05`, `AUTH-06`
- **Setup:** Clean test database; backend running.
- **Cleanup:** Preserve the newly created and verified account for Block 2.

### Block 2 — Onboarding & Settings
- **Cases:** `ONBOARD-01`, `SETTINGS-01`, `SETTINGS-02`, `SETTINGS-03`, `SETTINGS-04`, `SETTINGS-05`, `SETTINGS-06`
- **Setup:** Use verified account from Block 1 at `/onboarding`.
- **Cleanup:** Leave settings configured with 25/5 defaults, Tokyo/London weather, and auto season. Preserve state for Block 3.

### Block 3 — Saved Plan UI
- **Cases:** `TODAY-UI-01`, `TODAY-UI-02`, `TODAY-UI-03`, `TODAY-UI-04`, `TODAY-UI-05`
- **Setup:** Ensure current day has no plan for `TODAY-UI-01`, then insert/stage a valid daily plan for `TODAY-UI-02` through `TODAY-UI-05`.
- **Cleanup:** Preserve active tasks for focus sessions in Block 4.

### Block 4 — Pomodoro & Focus Execution
- **Cases:** `FOCUS-01`, `FOCUS-02`, `FOCUS-03`, `FOCUS-04`, `FOCUS-05`, `FOCUS-06`
- **Setup:** Main window and widget running on desktop. Select upcoming task from Block 3.
- **Cleanup:** Allow session to reach completion or pause state for Block 5.

### Block 5 — Replanning & Outcomes
- **Cases:** `REPLAN-01`, `REPLAN-02`, `REPLAN-03`, `REPLAN-04`, `REPLAN-05`
- **Setup:** Focus session in ending outcome prompt state.
- **Cleanup:** Verify rewards staged into database for verification in Block 6.

### Block 6 — Rewards, Garden, & Plant Unlocks
- **Cases:** `WATER-01`, `WATER-02`, `WATER-03`, `LEAF-01`, `LEAF-02`, `LEAF-03`, `GARDEN-01`, `GARDEN-02`, `GARDEN-03`, `GARDEN-04`, `GARDEN-05`, `PLANT-01`, `PLANT-02`, `PLANT-03`, `PLANT-04`, `PLANT-05`
- **Setup:** Use accumulated Water and Leaves from Blocks 4 and 5.
- **Cleanup:** Ensure active plant is set to Monstera or Sunflower for Widget tests.

### Block 7 — Goals & Milestone Reminders
- **Cases:** `GOAL-UI-01`, `GOAL-UI-02`, `GOAL-UI-03`, `GOAL-UI-04`, `GOAL-UI-05`, `REMINDER-01`, `REMINDER-02`, `REMINDER-03`, `REMINDER-04`, `REMINDER-05`
- **Setup:** Navigate to `/goals`. Create test goal with 3 milestones.
- **Cleanup:** Clear due reminders so tray icon returns to normal.

### Block 8 — Ambient Environment & Weather
- **Cases:** `SEASON-01`, `TIME-01`, `WEATHER-01`, `WEATHER-02`, `AMBIENT-01`
- **Setup:** Use `/widget-preview` and Settings general panel overrides.
- **Cleanup:** Restore season override to `AUTO` and weather to enabled.

### Block 9 — Desktop Widget & Tauri Lifecycle
- **Cases:** `WIDGET-01`, `WIDGET-02`, `WIDGET-03`, `WIDGET-04`, `WIDGET-05`, `WIDGET-06`, `DESKTOP-01`, `DESKTOP-02`, `DESKTOP-03`, `DESKTOP-04`
- **Setup:** Run in native Tauri desktop environment (`npm run tauri dev`).
- **Cleanup:** Re-open main window if hidden.

### Block 10 — Statistics, Failure, & Security Isolation
- **Cases:** `STATS-01`, `STATS-02`, `STATS-03`, `STATS-04`, `FAILURE-APP-01`, `FAILURE-APP-02`, `FAILURE-APP-03`, `FAILURE-APP-04`, `SECURITY-APP-01`, `SECURITY-APP-02`, `SECURITY-APP-03`
- **Setup:** Log into primary account `User A` to check statistics. Introduce secondary account `User B` for security isolation checks.
- **Cleanup:** Close test connections and terminate test processes.

