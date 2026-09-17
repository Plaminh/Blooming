# API Contracts and Data Model Mapping

## Contract Standardization (Shared API)
Currently, frontend features inconsistently prefix their API calls (`/api/v1/me`, `/today`, `/api/garden`, `/v1/statistics`). 
**Solution**: 
Update `PUBLIC_API_BASE_URL` in the frontend `.env` to point to the base domain (e.g., `http://127.0.0.1:8000/api/v1`).
Update `frontend/src/lib/api.ts` to automatically strip redundant prefixes (`/api/v1`, `/v1`, `/api`) from feature calls, ensuring all requests uniformly target the `API_V1_PREFIX`.

## Mappings per Feature

### 1. Authentication
- **Mock/Store Replaced**: Local session logic and `/api/v1/me` fetch in `authStore.ts`.
- **Backend Router**: `auth.py` and `users.py` (`/auth/login`, `/auth/register`, `/users/me`).
- **State Handling**: Successful login persists JWT. 401 Unauthorized clears local session and redirects to `/auth`.

### 2. Onboarding
- **Mock/Store Replaced**: `onboarding-preview/+page.svelte` alerts and `OnboardingSetupState.svelte.ts`.
- **Backend Router**: `user_settings.py` (`PUT /me/settings`).
- **Contract Mismatch Fix**: Map frontend fields to match backend schema:
  - `mrBloomName` -> `mr_bloom_display_name`
  - `focusDurationMinutes` -> `default_focus_minutes`
  - `breakDurationMinutes` -> `default_break_minutes`
  - `startAtLogin` -> `launch_on_startup`
  - `keepWidgetOnTop` -> `widget_always_on_top`
  - (Drop `milestone_reminder_time` and `email_reminders` as unsupported by MVP schema).

### 3. Today & Focus
- **Mock/Store Replaced**: Hardcoded `referenceTasks` and `/today?date=...` in `today/+page.svelte`.
- **Backend Router**: `today.py` (`GET /today`, `PATCH /today/tasks/{id}`) and `focus.py` (`POST /focus/start`, `POST /focus/finish`).
- **State Handling**: Timer runs locally. `POST /focus/start` is called on play. `POST /focus/finish` is called when timer concludes or is cancelled. If failure occurs, UI reverts gracefully without applying fake data.

### 4. Goals and Milestones
- **Mock/Store Replaced**: Mock calls in `goalsStore.ts` (currently pointing to `/goals/` instead of `/api/v1/goals`).
- **Backend Router**: `goals.py` (`GET /goals`, `POST /goals`, `PUT /goals/{id}`).
- **State Handling**: Frontend automatically updates local lists upon successful mutations, or triggers a refetch of `/goals` and `/reminders/due`.

### 5. Garden
- **Mock/Store Replaced**: Mock states and `/api/garden` in `garden-selection/model/state.svelte.ts`.
- **Backend Router**: `garden.py` (`GET /garden`, `POST /garden/plants/{id}/unlock`, `POST /garden/water`).
- **State Handling**: Garden actions are optimistic but must revert state and expose `error` to the user if the transaction is rejected (e.g. lack of currency).

### 6. Settings
- **Mock/Store Replaced**: `SettingsState.svelte.ts` mapping mismatch and `setTimeout` mock duration.
- **Backend Router**: `user_settings.py` (`GET /me/settings`, `PUT /me/settings`).
- **Contract Fix**: Align properties identically to the Onboarding fix described above. Remove the arbitrary `setTimeout` delay on save.

### 7. Statistics
- **Mock/Store Replaced**: Inconsistent `api.get('/v1/statistics/...')` in `statistics.api.ts`.
- **Backend Router**: `statistics.py` (`GET /statistics/summary`, `GET /statistics/daily`, `GET /statistics/plan-history`).
- **State Handling**: Legitimate zero values returned from the backend (e.g., zero completed tasks) must render normally. Empty backend arrays trigger the empty state view.

## Error and Shared State Handling
All API interactions through `api.ts` will trap network errors and throw an `APIError` instance exposing the status and detail.
- **Loading**: Use Svelte `{#if isPending}` blocks natively in organisms.
- **Validation (422)**: Surface error messages inline inside forms using the `detail` array from Pydantic.
- **Not Found (404)**: Redirect to today screen or show generic 'Resource Not Found' message.
- **Conflict (409)**: Alert the user of concurrent modifications or invalid domain actions.
