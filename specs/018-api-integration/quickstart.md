# Validation and Quickstart Guide

This guide describes how to validate the completed frontend API integration against the local backend server.

## Prerequisites

1. Ensure the PostgreSQL database is running and migrated to the latest schema:
   ```bash
   cd backend
   alembic upgrade head
   ```
2. Start the FastAPI backend server:
   ```bash
   cd backend
   python run.py
   ```
3. Start the SvelteKit frontend server:
   ```bash
   cd frontend
   npm run dev
   ```

## End-to-End Validation Scenarios

### 1. Authentication & Session Verification
1. Open the application in the browser or Tauri.
2. If signed out, fill out the registration form.
3. Observe successful registration and automatic sign in (or verify email if required by the backend flow).
4. Reload the page; the session must restore seamlessly via `localStorage` and valid JWT.
5. Provide a wrong password intentionally and verify that a red 401 error message displays instead of a silent failure.

### 2. Onboarding to Today Flow
1. As a new user, complete the onboarding setup screen.
2. Select a focus preset and submit.
3. Verify via `Network` tab that `PUT /api/v1/me/settings` receives the correctly mapped fields (`mr_bloom_display_name`, `default_focus_minutes`, etc.).
4. Proceed to the Today screen and create a new task. Verify `POST /api/v1/planning/tasks` or the relevant Today route is called.

### 3. Pomodoro Focus Consistency
1. On the Today screen, start a focus timer.
2. Verify `POST /api/v1/focus/start` is fired immediately.
3. Let the timer count down to completion (or fast forward/cancel).
4. Verify `POST /api/v1/focus/finish` is fired exactly once.
5. Navigate to the Statistics screen and verify the completed session time is aggregated correctly.

### 4. Settings Persistence
1. Navigate to Settings.
2. Change the Mr. Bloom Display Name and save.
3. Observe no artificial `setTimeout` delay; the save happens at real network speed.
4. Refresh the application completely and return to Settings to confirm the new name loads.

### 5. Garden Transactions
1. Ensure your account lacks currency (e.g., brand new account).
2. Attempt to unlock a plant. The action should fail with an appropriate toast/error message, and the plant remains locked.
3. Complete a long focus session to earn currency, then return and attempt the unlock again. It should succeed and deduct the currency visually.

## Automated Verification
Run the following checks to confirm the integration did not break existing type safety or standard practices:

- **Type Check**: `cd frontend && npm run check`
- **Linting**: `cd frontend && npm run lint`
- **Unit Tests**: `cd frontend && npm run test`
- **Build**: `cd frontend && npm run build` (Ensures static adapter compatibility)
