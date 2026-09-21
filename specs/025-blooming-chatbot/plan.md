# Implementation Plan: Blooming Multi-Tier Chatbot

**Branch**: `025-blooming-chatbot` | **Date**: 2026-09-20 | **Spec**: [specs/025-blooming-chatbot/spec.md](file:///E:/Blooming/specs/025-blooming-chatbot/spec.md)

**Input**: Feature specification from `/specs/025-blooming-chatbot/spec.md`

## Summary
The goal is to implement a multi-tier, zero-cost architecture for the "Mr. Bloom" planning assistant. The system will leverage deterministic routing, parsing rules, and small free-tier LLMs for fallback behavior, falling back to rule-based generation when token budgets are exhausted, while decoupling presentation from strict domain validation.

## Technical Context
**Language/Version**: Python 3.11, Rust 1.75, SvelteKit (Svelte 5.56)
**Primary Dependencies**: FastAPI, Pydantic, SQLAlchemy, Vite, Tauri 2
**Storage**: PostgreSQL
**Testing**: pytest (backend), vitest (frontend)
**Target Platform**: Linux backend, Windows/Linux Desktop shell
**Project Type**: Web API backend + Desktop App frontend
**Performance Goals**: Sub 1.5s latency on quota exhaustion (circuit breaker fallback).
**Constraints**: Zero-dollar budget (Ollama local fallback + Groq API limits).
**Scale/Scope**: Focus on stable, persistent daily planning sessions.

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*
- [x] Does the plan align with the Spec-driven development workflow?
- [x] Does the plan preserve the approved boundaries?
- [x] Does deterministic application code remain authoritative?
- [x] Are explicit contracts and type safety boundaries defined?
- [x] Is the proposed implementation the simplest that satisfies the spec?
- [x] Are testable behavior and quality gates defined?
- [x] Does the UX handle loading, partial, and failure states gracefully?
- [x] Are resource efficiency and platform scope strictly followed?
- [x] Are security and privacy principles respected?

## Project Structure
### Documentation
```text
specs/025-blooming-chatbot/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
    ├── assistant.md
    └── goal.md
```

### Source Code
**Backend**: Modular Monolith
```text
backend/app/
├── ai/
│   ├── providers.py
│   ├── budget.py
│   ├── router.py
│   ├── orchestrator.py
│   ├── parser.py
│   └── handlers/
├── api/routes/assistant.py
├── schemas/drafts.py
└── db/models/ai_usage.py
```
**Frontend**: Svelte 5 Feature Modules
```text
frontend/src/lib/features/mr-bloom/
├── components/
│   ├── molecules/
│   └── organisms/
└── model/
```

## Delivery Stages (PRs 1-14)

### PR 1: Phase 0 Backend Foundation (Provider, Config, Logs)
- **Objective/Milestone**: A resilient LLM provider layer using circuit breakers and quota-based degradation.
- **Files**: Add `app/ai/providers.py`, `app/ai/budget.py`, `app/db/models/ai_usage.py`, `alembic/versions/xxx_ai_usage.py`. Modify `app/core/config.py`, `app/main.py`.
- **Involved**: `ai_usage_log` table, `init_ai_client()`, `LLMError`, `chat_rate_limit`.
- **Flags/Fallbacks**: Configure `OLLAMA_BASE_URL` vs `GROQ_BASE_URL`. Falls back cleanly with `HTTPException` gracefully handled by orchestrator.
- **Tests**: `test_providers.py`, `test_budget.py`, `test_rate_limit.py`. Manual test: invalid JSON and 429 Retry-After parsing.
- **Security**: No PII in `ai_usage_log`. Keep keys in `.env`.
- **Completion Gate**: `pytest` passes. `Ollama` endpoint can be queried successfully.

### PR 2: Phase 0 Frontend Correctness Fixes
- **Objective/Milestone**: Chat UI handles IME safely, scrolls correctly, and processes retries.
- **Files**: Modify `ChatMessage.svelte`, `ChatComposer.svelte`, `MrBloomConversationPanel.svelte`, `mrBloomStore.ts`.
- **Involved**: UI interaction handlers, `bind:this` for scrolling, `e.isComposing`.
- **Tests**: `vitest` for component state isolation.

### PR 3: Canonical Drafts and Scheduler Data Preservation
- **Objective/Milestone**: Server-side definitions for `TodayDraft` and `RoadmapDraft` that correctly map domain tasks.
- **Files**: Modify `app/schemas/drafts.py`, `app/services/today_service.py`. Remove duplicated frontend schemas.
- **Involved**: `TaskDraft`, `TodayDraft`, `_normalize_and_schedule`. Maps `breakAfterMin` properly to scheduler payload.
- **Tests**: `test_planner_assemble.py`, `test_today_preview.py`.

### PR 4: Router, Rules Handlers, Template Chitchat
- **Objective/Milestone**: 0-token deterministic routing for STATUS, GREETING, CHITCHAT.
- **Files**: Add `app/ai/router.py`, `app/ai/handlers/rules.py`, `app/ai/handlers/chitchat.py`, `app/ai/knowledge.py`.
- **Involved**: Intent regex matching, bilingual templates.
- **Tests**: `test_router_rules.py`, `test_chitchat.py`, 50 cases of language parsing.
- **Completion Gate**: A simple "Hello" request uses 0 tokens and responds via rules.

### PR 5: Deterministic Parser and Scheduler Preview Coach
- **Objective/Milestone**: Extracts plan components (`PLAN_DAY`) via regex when possible, bypassing LLM entirely for simple prompts.
- **Files**: Add `app/ai/parser.py`, `app/ai/estimates.py`, `app/ai/validators.py`.
- **Involved**: Regex for "1h30m", "từ 9h", etc. `estimates.py` keyword lookups.
- **Tests**: `test_parser.py`, `test_estimates.py`, `test_validators.py`.

### PR 6: Frontend Real Preview/Save Integration
- **Objective/Milestone**: Replace fake timelines with real API preview states.
- **Files**: Modify `TimelineDraftPreview.svelte`, `PlanDraftPreview.svelte`, `api.ts`, `mrBloomStore.ts`.
- **Involved**: `$state`, `previewTodayPlan()`, debounce timers.
- **Completion Gate**: Clicking SAVE successfully submits the HMAC token and registers a new day plan.

### PR 7: LLM Planner Cascade and Bounded Repair
- **Objective/Milestone**: Fallback for ambiguous text; 8B model handles what parser can't, cascading to large model on failure.
- **Files**: Add `app/ai/handlers/planner.py`, `app/ai/orchestrator.py`.
- **Involved**: `complete_json` with cascaded retries. Max 1 repair run on validation failure.
- **Tests**: `test_cascade.py` showing 8B -> 20B fallback flow.

### PR 8: Usage Log, Budget Guard, Modes, and Degraded Banner
- **Objective/Milestone**: Read `ai_usage_log` sum for last 24h to flip `NORMAL` -> `LEAN` -> `RULES_ONLY` mode dynamically.
- **Files**: Modify `app/ai/budget.py`, `DegradedBanner.svelte`.
- **Involved**: Rolling sum query, UI banner.
- **Tests**: `test_usage_log.py` verifying no prompt injection or message recording.

### PR 9: Clarification, Roadmap Fallback, Goal Creation
- **Objective/Milestone**: Handle ambiguous missing values (e.g., target date for goal) with a single clarification question.
- **Files**: Add `app/ai/handlers/clarify.py`. Modify `app/services/goals_service.py` (`create_goal` and `POST /goals/from-roadmap`).
- **Tests**: Verify atomicity of Goal + Milestone insertion (rollback on failure).

### PR 10: Deterministic and LLM Patch Editor
- **Objective/Milestone**: Allow users to edit plans directly ("change task 2 to 45 mins") without full generation.
- **Files**: Add `app/ai/patches.py`, `app/ai/editor_rules.py`, `app/ai/handlers/editor.py`.
- **Involved**: `POST /assistant/apply-patch`.
- **Tests**: `test_patches.py` checking boundary enforcement.

### PR 11: Session and Message Persistence
- **Objective/Milestone**: Persist conversations seamlessly via existing db tables.
- **Files**: Modify `app/api/routes/assistant.py` to write to `planning_sessions` & `messages`.
- **Involved**: Immediate commits. Status tracking (`OPEN`, `COMPLETED`, `AWAITING_CLARIFICATION`).

### PR 12: Mood Handlers and Explicit Actions
- **Objective/Milestone**: Pre-defined rules for tiredness and quick-reply action handling.
- **Files**: Add `app/ai/handlers/mood.py`. Add `POST /assistant/actions/{name}`.
- **Involved**: `SKIP_OPTIONAL_TODAY` mutation action.
- **Tests**: Crisis precedence keyword interception testing.

### PR 13: Historical Calibration
- **Objective/Milestone**: Re-adjust future task estimates based on `FocusRun` actual durations compared to estimates.
- **Files**: Add `app/ai/calibration.py`. Modify `TaskDraft`.
- **Tests**: `test_calibration.py` ensuring statistical significance formula (e.g. `n >= 5`).

### PR 14: Proactive Event-Driven Nudges
- **Objective/Milestone**: Send users discrete UI suggestions when behind schedule.
- **Files**: Add `app/ai/proactive.py`.
- **Involved**: Desktop window `emitTo` from Tauri, deduplication using `getCurrentWindow()`.
- **Tests**: `test_proactive.py` verifying quiet-hours and cooldown rules.
