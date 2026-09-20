# Quickstart Validation Guide

## Prerequisites
- Backend environment set up (Python 3.10+, pip)
- Frontend environment set up (Node.js, npm)
- `GROQ_API_KEY` defined in `.env` (can be a fake key for testing error handling)

## Backend Validation
To verify all backend behaviors (Rate Limiting, Schema Migration, LLM Client Initialization, Draft Validation/Repair):

```bash
cd backend
# Run focused tests for assistant behavior
pytest tests/unit/test_assistant_service.py
pytest tests/unit/test_assistant_schemas.py

# Run full test suite
pytest

# Run type checks / linting
mypy app
ruff check app
```

**Expected Outcome**: 
- `test_assistant_service.py` passes, proving that missing API keys return a 503, rate limits return a 429, timeouts return a 504, and bad JSON returns 502, without leaking secrets in logs.
- `test_assistant_schemas.py` passes, proving that invalid drafts are correctly repaired or discarded while preserving valid reply text, and timezones/dates are correctly assigned from server context.
- `mypy` and `ruff` pass without errors.

## Frontend Validation
To verify frontend fixes (Auto-scroll, Multiline rendering, IME Enter handling, Dynamic Greeting):

```bash
cd frontend
# Run unit tests for mr-bloom components and stores
npm run test -- run src/lib/features/mr-bloom

# Run Svelte checks
npm run check
```

**Expected Outcome**: 
- Vitest output shows all tests passing, proving that composing enter does not submit, shift+enter creates a newline, and retry does not duplicate user messages.
- `npm run check` returns no warnings or errors.

## Manual Smoke-Test Steps
1. **Invalid API Key**: Set a fake `GROQ_API_KEY` in `.env`, run the app, and attempt to chat. You should see a gracefully handled error in the UI.
2. **Multiline & Shift-Enter**: Type a message in the chat box, press Shift+Enter, and ensure a newline is inserted instead of submitting. Submit it and verify the chat bubble renders the multiple lines correctly.
3. **Dynamic Greeting**: Refresh the app to ensure the initial assistant message reflects the current local time (e.g. "Good evening").
4. **Valid Interaction**: Provide a valid `GROQ_API_KEY`, ask for a schedule, and verify the schedule renders properly and timezones match your system clock without shifting dates.
