# Integration contracts

## Today

`GET /api/v1/today?date=YYYY-MM-DD` returns plan date/status and blocks (or NO_PLAN). Task blocks expose nullable category/description and estimated_duration_minutes.

`PATCH /api/v1/today/tasks/{task_id}` accepts optional title (1-200 chars), estimated_duration_minutes (1-10080), description (string or null), category (Learning/Work/Personal/null). Omitted fields are preserved; explicit null clears notes/category. Returns the typed TaskResponse. The edit form retains the draft and displays an accessible error on failure.

`POST /api/v1/today/replan` takes no body and uses today's date in UserSettings.timezone. It returns the Today response. Completed/active/locked/fixed and terminal blocks are preserved. Eligible unfinished flexible work uses deterministic scheduling around reserved intervals. Insufficient capacity/dependency failures return a visible API error without deleting work. Concurrent requests are serialized on the user row; UI duplicate calls are guarded.

## Garden

`GET /api/v1/garden` returns water_balance, leaves_balance, selected_plant_id, catalog, vitality, growth_points and `growth_stage`. Stages: SPROUTING 0-99, GROWING 100-299, BLOOMING 300-699, FLOURISHING 700+. No FRUITING in this response contract. Persisted legacy stage remains untouched. Garden selection uses the selected plant ID; sprite mapping uses inspected species atlas, growth stage and vitality.

## Settings and reminders

`GET /api/v1/me/settings` and `PUT /api/v1/me/settings` expose milestone_reminder_lead_time_minutes: integer 0-43200, default 1440. Zero means at deadline. UI offers deadline, one hour, one day, three days before. No reminder-time localStorage setting.

`GET /api/v1/reminders/due` respects reminders_enabled and, only when quiet_hours_enabled is true, UserSettings.timezone and the configured wall-clock interval. Start inclusive, end exclusive; equal endpoints are an empty interval; invalid IANA timezone falls back to UTC. Suppression leaves status untouched.

Creation, deadline/title/status edits, MOVE_MILESTONE actions and lead-time settings changes synchronize a single milestone reminder: original_due_at = milestone deadline; due_at = deadline minus lead time. REMIND_LATER changes delivery time only.

## Desktop

One typed wrapper in `frontend/src/lib/platform/desktopWindow.ts`. `blooming:schedule-updated` carries null and refreshes widget/session/garden data following successful operations. No browser CustomEvent transport. Native settings read actual autostart/always-on-top state, apply saved state and verify it. Native failures stay visible and prevent save success.

Rust command `set_tray_icon(alert: bool)` returns Result<(), String>. Exactly one tray uses bundled normal/red-dot assets. Left click shows, unminimizes and focuses main. Application-root polling belongs to the companion window, including while hidden. No native popup or Rust scheduler.
