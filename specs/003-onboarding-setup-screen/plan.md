# Implementation Plan: onboarding-setup-screen

**Branch**: `003-onboarding-setup-screen` | **Date**: 2026-09-13 | **Spec**: [specs/003-onboarding-setup-screen/spec.md](specs/003-onboarding-setup-screen/spec.md)

**Input**: Feature specification from `specs/003-onboarding-setup-screen/spec.md`

## Summary

Create a standalone onboarding setup screen following Atomic Design principles, preserving the existing pixel-art style, and utilizing local state management. The screen consists of a two-column layout featuring an illustrated branding panel on the left and a setup form on the right. All state is maintained locally without backend changes.

## Technical Context

**Language/Version**: TypeScript, Svelte 5

**Primary Dependencies**: SvelteKit

**Storage**: N/A (Local component state only)

**Testing**: Vitest (existing frontend testing framework)

**Target Platform**: Desktop App (Frontend View)

**Project Type**: Svelte Component Module

**Performance Goals**: N/A (Standard UI rendering)

**Constraints**: Must perfectly match the reference design, keep state local, avoid backend modifications.

**Scale/Scope**: Single screen setup view.

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
specs/003-onboarding-setup-screen/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command - NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── lib/
│   │   ├── features/
│   │   │   └── onboarding-setup/
│   │   │       ├── components/
│   │   │       │   ├── atoms/
│   │   │       │   ├── molecules/
│   │   │       │   ├── organisms/
│   │   │       │   └── pages/
│   │   │       │       └── OnboardingSetupView.svelte
│   │   │       └── model/
│   │   └── shared/
│   │       └── styles/
│   │           └── theme.css
│   └── routes/
│       └── onboarding-preview/
```

**Structure Decision**: Feature module `onboarding-setup` under `frontend/src/lib/features/` using Atomic Design (`atoms`, `molecules`, `organisms`, `pages`) plus a local `model/`. Shared visual tokens live in `frontend/src/lib/shared/styles/theme.css` (`--bloom-*`). `/onboarding-preview` is a development-only visual test route.
