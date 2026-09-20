import os

content = """# Research: Blooming Multi-Tier Chatbot MVP

## Technical Context

- **Language/Version**: Python 3.11, SvelteKit/TypeScript
- **Primary Dependencies**: FastAPI, Pydantic, httpx
- **Storage**: PostgreSQL (via SQLAlchemy/Alembic)
- **Testing**: pytest (backend), vitest (frontend)
- **Target Platform**: Desktop (Tauri) / Local Web
- **Project Type**: Local-first productivity app with cloud AI
- **Performance Goals**: 0 token baseline for simple interactions, <1.5s latency overhead for LLM fallback.

## Verified Current Architecture

1. **Provider Layer**: `backend/app/services/assistant_service.py` currently handles `_call_llm` via `httpx.AsyncClient` directly, reading `GROQ_BASE_URL` from config. Repair logic (1 validation retry) is currently baked into the service. `backend/app/ai/` directory does not exist.
2. **Canonical Drafts**: `backend/app/schemas/drafts.py` contains `TodayDraft` and `RoadmapDraft` but is not fully integrated with a true `/today/preview` endpoint in the assistant chat loop. Frontend still has duplicate types in `mrBloomStore.ts`.
3. **Persistence**: `planning_sessions` and `planning_messages` tables exist but are not yet used by the chatbot for real session persistence.
4. **Database & Settings**: Database migrations exist, managed by Alembic. `users` table exists. `UserSettings` exists but does not have `workday_start` or `workday_end`.

## Resolved Decisions

### Provider Abstraction Boundary
- **Decision**: Create `backend/app/ai/providers.py` to abstract HTTP logic. Use `json_schema` with `strict: True` for OpenAI-compatible models when explicitly configured via `AI_STRICT_MODELS` list, falling back to `json_object` + validator for others (e.g., Llama). `reasoning_effort` will be passed only to O-series/GPT-OSS equivalent models.
- **Rationale**: Replaces direct `httpx.AsyncClient` usage in `assistant_service.py` to allow multi-model cascading and deterministic fallbacks (Phase 0 requirement).

### Budget and Observability
- **Decision**: Introduce `ai_usage_log` table with `user_id, purpose, provider, model, tokens, latency, outcome`. Enforce 24-hour sliding window budget at the application level.
- **Rationale**: Fulfills the `RULES_ONLY` fallback constraint by keeping a precise token ledger without exposing PII (Phase 4 requirement).

### Schemas & Contracts
- **Decision**: Update `ChatResponse` in `schemas/assistant.py` to include `degraded`, `preview`, `assumptions`, `suggestions`, and `intent/tier` metadata. All domain objects use canonical forms from `schemas/drafts.py`.
- **Rationale**: Removes circular dependencies. Centralizes parsing.

### Routing & Parser
- **Decision**: Build deterministic intent matcher in `backend/app/ai/router.py` using normalized text matching before relying on an LLM classifier. Extract simple times (e.g., `30p`, `1h`) using regex.
- **Rationale**: Zero-LLM baseline.

### Persistence
- **Decision**: Persist `planning_messages` immediately before LLM call, and update after response. Re-use existing `planning_sessions`.
- **Rationale**: Ensures chat state recovery even if LLM rate-limits or crashes.

### Frontend Store Integration
- **Decision**: Delete duplicated types in `mrBloomStore.ts` and fetch generated API types. Use server-provided `preview` property to render the timeline rather than local `generateTimeline()` calculations.
- **Rationale**: SSOT (Single Source of Truth) architecture.

## Known Conflicts & Resolutions

- **Conflict**: Embedded plan suggests Groq provides Llama-3.1-8b-instant with `strict: True` support.
- **Resolution**: We will conditionally apply `strict: True` only for models listed in `AI_STRICT_MODELS`, assuming Groq's Open-Source models might not all support it. This prevents 400 errors.
- **Conflict**: Embedded plan expects `focus_runs.actual_duration_seconds` for historical calibration.
- **Resolution**: Will verify if this column exists, and write the appropriate `ai_usage` migration.

## Deferred Items

- **BYOK (Section 14)**: Explicitly deferred as requested.
- **Feature Flag Logic**: Tiers will be controlled via config, but not a full feature flagging server.
"""

with open(r"E:\Blooming\specs\025-blooming-chatbot\research.md", "w", encoding="utf-8") as f:
    f.write(content)
