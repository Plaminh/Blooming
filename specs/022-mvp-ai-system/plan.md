# Implementation Plan: MVP AI System

**Branch**: `[022-mvp-ai-system]` | **Date**: 2026-09-19 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/022-mvp-ai-system/spec.md`

## Summary

The MVP AI system implements an intelligent routing layer for user planning inputs. It first attempts deterministic rule-based parsing. If unresolved, it routes to Groq (primary LLM) and falls back to Gemini via Cloudflare AI Gateway. It guarantees all AI output passes strict Pydantic schemas and business validations before returning a DraftProposal for user confirmation, ensuring zero direct AI mutation of authoritative application state.

## Technical Context

**Language/Version**: Python 3.11, TypeScript (SvelteKit)

**Primary Dependencies**: FastAPI, Pydantic, httpx

**Storage**: PostgreSQL (via SQLAlchemy) - *Read-only for AI*

**Testing**: pytest, httpx test client

**Target Platform**: Desktop app backend (Windows/Linux)

**Project Type**: backend service

**Performance Goals**: < 50ms for rule-based parsing, < 5s for primary AI inference

**Constraints**: Fallbacks must trigger automatically on unusable structured outputs, AI output must pass strict Pydantic schema validation.

**Scale/Scope**: Local desktop single-user

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
specs/022-mvp-ai-system/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
backend/
├── app/
│   ├── api/
│   │   └── routes/
│   │       └── planning.py
│   ├── services/
│   │   ├── ai_router.py
│   │   ├── ai_provider.py
│   │   ├── rule_parser.py
│   │   ├── business_validator.py
│   │   ├── groq_provider.py
│   │   └── gemini_provider.py
│   └── models/
│       └── ai_schemas.py
└── tests/
    ├── services/
    │   ├── test_ai_router.py
    │   ├── test_business_validator.py
    │   ├── test_groq_provider.py
    │   └── test_gemini_provider.py
    ├── api/
    │   └── test_planning_ai_api.py
    └── unit/
        └── test_rule_parser.py
```

**Structure Decision**: The AI routing logic is isolated within the `backend/app/services` directory, maintaining the clear boundary between the presentation layer (SvelteKit) and the business logic layer (FastAPI), adhering to the project's modular monolith architecture.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No constitution violations detected.
