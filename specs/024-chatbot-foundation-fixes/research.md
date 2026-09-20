# Phase 0 Technical Research

## FastApi Application Lifecycle
- **Startup/Shutdown**: Uses `@asynccontextmanager` `lifespan` in `backend/app/main.py`. This is the designated place to initialize and cleanly close the shared `httpx.AsyncClient`.

## Configuration
- **Settings**: Handled by `pydantic_settings.BaseSettings` in `backend/app/core/config.py`. Environment variables are loaded from `.env`. We will add the required AI variables here.

## Groq / LLM Client
- **Current State**: `assistant_service.py` currently instantiates a new `httpx.AsyncClient(timeout=30.0)` for every single request.
- **Decision**: Introduce a global/shared HTTP client injected or initialized during `lifespan` and imported into `assistant_service.py`.

## Assistant Route and Validation
- **Flow**: `/assistant/chat` -> `assistant_service.chat`.
- **Validation**: `ChatResponse.model_validate_json(content)` validates the entire block. If the draft part fails, `ValidationError` is raised and caught by a generic handler, returning 502 and losing the reply.
- **Decision**: Parse JSON to dictionary. Extract `reply`. Validate `draft` independently. If invalid, run the one-attempt repair. If that fails, set `draft = None` but keep `reply`.

## Draft Models & Circular Imports
- **Current**: `backend/app/schemas/today.py` imports `TodayDraft` from `backend/app/schemas/assistant.py`.
- **Decision**: Move shared draft schemas (`TodayDraft`, `AvailabilityWindowDraft`, `TaskDraft`, `RoadmapDraft`, `MilestoneDraft`) into a new `backend/app/schemas/drafts.py` module to eliminate circular imports.

## Timezone and Absolute Dates
- **Current**: `TodayDraft` defaults to `UTC`. It's populated by LLM.
- **Decision**: Remove LLM's authority to populate `timezone`. Populate it deterministically using server-side settings (e.g. from `CurrentUser` settings).

## Rate Limiting
- **Current**: No chat rate limiting.
- **Decision**: Implement a per-user token bucket or sliding window in-memory limiter scoped to the `/assistant/chat` route using FastAPI dependency injection.

## Frontend Chat State
- **Store**: `frontend/src/lib/features/mr-bloom/stores/mrBloomStore.ts` uses Svelte stores.
- **Greeting**: Hardcoded to `Good morning.\n...` at `09:00`.
- **Composer**: `ChatComposer.svelte` binds `onkeydown` for Enter. Will update to check `!e.isComposing` and `!e.shiftKey`.
- **Message Rendering**: `ChatMessage.svelte` requires `white-space: pre-wrap`.
- **Retry Logic**: `submitMessage` pushes the user message, and on error leaves it there and sets a global `error`. To support retry without duplication, we need to add a `status: 'failed'` to `ChatMessage` and exclude failed messages when building the outgoing `history` array.
