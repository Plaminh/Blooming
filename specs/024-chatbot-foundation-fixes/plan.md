# Implementation Plan: Chatbot Foundation Fixes (Phase 0)

**Branch**: `[024-chatbot-foundation-fixes]` | **Date**: 2026-09-20 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `/specs/024-chatbot-foundation-fixes/spec.md`

## Summary

This Phase 0 implementation repairs and secures the foundational assistant chat behavior. It centralizes and manages the LLM HTTP client (Groq) correctly in the FastAPI lifecycle, resolves model circular dependencies via a canonical drafts module, adds MVP rate limiting, maps LLM and network errors properly without failing valid replies, and fixes several chat frontend glitches (auto-scroll, multiline text, retry, dynamic greeting).

## Technical Context

**Language/Version**: Python 3.10+, TypeScript, Svelte 5

**Primary Dependencies**: FastAPI, Pydantic, SvelteKit, `httpx`

**Storage**: PostgreSQL (No migrations required for Phase 0)

**Testing**: Pytest (backend), Vitest + Svelte Check (frontend)

**Target Platform**: Desktop app (Tauri 2 / Rust), with a FastAPI backend.

**Project Type**: Desktop application with local Web API.

**Performance Goals**: LLM chat endpoints must safely handle timeouts (30s max), rate limits (per 60s window), and not leak resources.

**Constraints**: Strict timezone and absolute date mapping must occur on the server. AI output is untrusted and must be schema-validated.

**Scale/Scope**: Single authenticated user per process (local MVP scale).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Does the plan align with the Spec-driven development workflow?
- [x] Does the plan preserve the approved Tauri 2/Rust, SvelteKit/TypeScript/Vite, FastAPI/Python/Pydantic, and PostgreSQL/SQLAlchemy boundaries?
- [x] Does deterministic application code remain authoritative while AI output and external input are validated at trust boundaries?
- [x] Are explicit contracts and type safety boundaries defined?
- [x] Is the proposed implementation the simplest that satisfies the spec?
- [x] Are testable behavior and quality gates defined?
- [x] Does the UX handle loading, partial, and failure states gracefully?
- [x] Are resource efficiency and platform scope strictly followed?
- [x] Are security and privacy principles respected?

## Project Structure

### Documentation (this feature)

```text
specs/024-chatbot-foundation-fixes/
├── spec.md
├── plan.md              # This file
├── research.md          # Technical research findings
├── data-model.md        # Canonical schema migration details
├── quickstart.md        # End-to-end validation guide
└── tasks.md             # (To be generated next)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── api/routes/assistant.py
│   ├── core/config.py
│   ├── main.py
│   ├── schemas/
│   │   ├── assistant.py
│   │   ├── drafts.py     # NEW
│   │   └── today.py
│   └── services/assistant_service.py
└── tests/
    └── unit/
        ├── test_assistant_schemas.py
        └── test_assistant_service.py

frontend/
├── src/lib/features/mr-bloom/
│   ├── components/
│   │   ├── molecules/ChatComposer.svelte
│   │   └── molecules/ChatMessage.svelte
│   └── stores/mrBloomStore.ts
```

**Structure Decision**: Web application layout (backend/frontend). The backend API is modified to introduce `drafts.py`, inject dependencies, and update settings. The frontend touches specific `mr-bloom` UI components.

## Complexity Tracking

*(No violations to Constitution Check)*
