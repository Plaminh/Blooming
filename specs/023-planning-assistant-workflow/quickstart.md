# Quickstart Validation Guide

This guide validates the e2e flow of the planning assistant and the deterministic scheduler without relying on frontend fakes.

## Prerequisites
- Backend running locally (`uvicorn app.main:app --reload`)
- Frontend running locally (`npm run dev`)
- A valid `GROQ_API_KEY` set in the backend `.env`

## Scenario 1: Context-Aware Chat
1. Send a chat message: "I want to plan my day. I have 4 hours. Task 1: review PRs (30m). Task 2: Write feature (2h)."
2. **Verify**: The assistant responds with a `TodayDraft` JSON payload populated correctly. The response is validated by Pydantic.
3. Edit the draft via chat: "Change review PRs to 1 hour."
4. **Verify**: The assistant modifies the draft accordingly, utilizing the `current_draft` and `session_id`.

## Scenario 2: Scheduler Preview
1. Click "GENERATE TIMELINE" in the frontend.
2. **Verify**: The network tab shows a `POST /today/preview` request.
3. **Verify**: The UI renders blocks returned from the backend (`app.core.scheduler`) and does not synthesize its own timeline blocks.

## Scenario 3: Atomic Persistence
1. Click "SAVE TO TODAY".
2. **Verify**: `POST /today/save` is called and returns a `200 OK`.
3. **Verify**: The database contains exactly one new `DailyPlan` and its corresponding `Task` records.
4. **Verify**: The `DailyPlan` is linked to the active `PlanningSession`.
5. Refresh the page.
6. **Verify**: The scheduled timeline and chat history are restored correctly from the backend.
