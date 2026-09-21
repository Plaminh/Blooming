# Research: Blooming Chatbot Foundation

## 1. Verified Current Architecture
The current application consists of:
- **Desktop Shell/UI**: Tauri 2, SvelteKit, TypeScript, Vite.
- **Backend**: FastAPI, Python 3.11, Pydantic, SQLAlchemy, PostgreSQL.
- **AI Integration**: A single HTTP client inside `assistant_service.py` making calls to Groq API using `llama-3.1-8b-instant` or similar models. The current flow is monolithic, sending chat history and receiving a JSON response.
- **Scheduler**: The backend (`core/scheduler.py`) performs a deterministic topological sort to schedule tasks based on FIXED and FLEXIBLE types, resolving constraints and dependencies. `today_service.py` provides the integration (preview, save).
- **Authentication**: Backend authenticates the user, scopes DB queries, and provides `CurrentUser`.

## 2. Existing vs. Proposed Mapping
| Existing | Proposed | Notes |
|----------|----------|-------|
| `assistant_service.py` monolithic call | `ai/providers.py`, `ai/router.py`, `ai/orchestrator.py` | Break up into multi-tier rules, parsers, and LLM cascaded approach. |
| Nested single draft schema | Flattened `LLMTask` and `LLMDayPlan`, assembled server-side | LLMs perform better on flat schemas, deterministic rules build canonical nested drafts. |
| Frontend `generateTimeline` logic | Removal of fake timeline generation | Front-end relies entirely on `/today/preview` for timeline rendering. |
| Unpersisted session context | `planning_sessions` and `planning_messages` tables | Immediate commit of user message, persisting state and allowing for stateful conversations (e.g., pending clarification). |

## 3. Resolved Unknowns & Repository Evidence
- **FastAPI Lifespan**: `app.main.py` utilizes a simple lifespan manager `init_ai_client()` and `close_ai_client()`. This can easily be adapted for the shared provider layer.
- **Draft Schemas**: The assistant currently uses `ChatResponse` inside `assistant_service.py` importing from local assistant schemas. The proposed structure consolidates this under `drafts.py` to decouple LLM responses from domain canonical representations.
- **Database Schema**: `planning_sessions` and `planning_messages` already exist in the database with columns like `session_type`, `status`, and `structured_payload`. We can reuse these without major new migrations.

## 4. Provider Capability Assumptions
- We assume `llama-3.1-8b-instant` (or equivalent local model) is capable of basic intent classification and small JSON structures, though lacking strict structured output support. It will require `"type": "json_object"`.
- We assume `gpt-oss-20b`/`120b` (or equivalent) supports `strict: true` and `reasoning_effort="low"`.
- A manual verification gate is required before launch to confirm real limits from Groq settings.

## 5. Explicit Deferred Items
- **BYOK (Bring Your Own Key)**: This is explicitly deferred per the specification constraints. The MVP will rely on local inference (Ollama) or constrained Groq limits, utilizing the budget guard.

## 6. Blockers
- **None**: All implementation details resolve cleanly to existing structures or specified requirements.
