# Quickstart Validation Guide: Pomodoro and Re-planning

This guide provides steps to validate the Pomodoro and Re-planning feature end-to-end.

## Prerequisites

1. The backend server must be running (`npm run backend` or similar).
2. The Tauri desktop app must be running (`npm run tauri dev`).
3. You must have a planned day with at least two flexible tasks.

## Validation Scenarios

### Scenario 1: Start and Pause a Session

1. Open the Today screen in the desktop app.
2. Select a task and click the "Start Focus" button.
3. **Verify**: The Companion Widget appears, displaying a counting down timer.
4. Click the "Pause" button in the widget.
5. **Verify**: The timer stops.
6. Refresh the Today window.
7. **Verify**: The Companion Widget retains the paused timer state and doesn't lose the elapsed time.

### Scenario 2: Finish a Session successfully and Re-plan

1. Resume the previously paused session.
2. Click the "End" button (or let the timer reach zero).
3. Select the "Done" outcome.
4. **Verify**: The Companion Widget hides.
5. **Verify**: The task in the Today timeline is marked as completed (green/checked).
6. **Verify**: Any remaining future flexible tasks in the timeline have shifted their `planned_start_at` times to begin after the current time, reflecting the deterministic replan execution.

### Scenario 3: Verify Conflict Prevention

1. Start a new session from another task.
2. In a terminal, attempt to forcefully start a second session using `curl`:
   ```bash
   curl -X POST http://localhost:8000/api/v1/focus/start \
     -H "Authorization: Bearer <YOUR_TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"planned_focus_seconds": 1500, "planned_break_seconds": 300}'
   ```
3. **Verify**: The API returns a `400 Bad Request` with "An active focus session already exists".
