# Implementation Plan: Auth and User Settings

**Branch**: `[]` | **Date**: 2026-09-16 | **Spec**: [specs/012-auth-and-user-settings/spec.md](file:///E:/Blooming/specs/012-auth-and-user-settings/spec.md)

**Input**: Feature specification from `/specs/012-auth-and-user-settings/spec.md`

## Summary

Implement the first complete backend vertical slice for authentication (Register/Login via JWT) and user settings (Retrieval/Update). This requires setting up password hashing, token generation, API endpoints under `/api/v1`, and extending the existing `user_settings` table to support UI preferences.

## Technical Context

**Language/Version**: Python 3.10.10

**Primary Dependencies**: FastAPI, Pydantic, SQLAlchemy 2.x, Psycopg 3, Alembic, bcrypt, PyJWT

**Storage**: PostgreSQL (Async)

**Testing**: Manual acceptance validation (no automated tests)

**Target Platform**: Windows + Linux

**Project Type**: web-service (Backend API)

**Performance Goals**: N/A (Standard web response times)

**Constraints**: Must use async DB sessions. Do not implement native desktop behavior or modify Tauri/SvelteKit code.

**Scale/Scope**: Local phase (MVP user flows).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Does the plan align with the Spec-driven development workflow?
- [x] Does the plan preserve the approved Tauri 2/Rust, SvelteKit/TypeScript/Vite, FastAPI/Python/Pydantic, and PostgreSQL/SQLAlchemy boundaries?
- [x] Does deterministic application code remain authoritative while AI output and external input are validated at trust boundaries?
- [x] Are explicit contracts and type safety boundaries defined?
- [x] Is the proposed implementation the simplest that satisfies the spec?
- [x] Are testable behavior and quality gates defined?
- [x] Does the UX handle loading, partial, and failure states gracefully? (N/A for backend only)
- [x] Are resource efficiency and platform scope strictly followed?
- [x] Are security and privacy principles respected?

## Project Structure

### Documentation (this feature)

```text
specs/012-auth-and-user-settings/
├── plan.md              
├── research.md          
├── data-model.md        
├── quickstart.md        
├── contracts/           
└── tasks.md             
```

### Source Code (repository root)

```text
backend/
├── alembic/
│   └── versions/
│       └── [timestamp]_add_user_settings_ui_prefs.py
├── app/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   ├── users.py
│   │   │   └── user_settings.py
│   │   └── deps.py
│   ├── core/
│   │   ├── config.py
│   │   └── security.py
│   ├── db/
│   │   ├── models/
│   │   │   ├── users.py
│   │   │   └── ...
│   │   └── session.py
│   ├── schemas/
│   │   ├── user.py
│   │   ├── token.py
│   │   └── user_settings.py
│   └── services/
│       ├── auth_service.py
│       ├── user_service.py
│       └── user_settings_service.py
```

**Structure Decision**: Standard FastAPI web application layout matching the existing repository structure (separated into routers, schemas, services, and core modules).


