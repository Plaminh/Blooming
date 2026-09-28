# Pre-Refactor Architecture Map

## Overview
The Blooming repository currently operates as a monorepo containing a Python/FastAPI backend, a Svelte 5 frontend, and Tauri desktop bindings. 

## Key Issues Addressed by Refactor

### Frontend
- **Current State**: Feature components and shared primitives are mixed. State stores are large and centralized, handling multiple responsibilities. Deep hierarchies in `atoms/`, `molecules/`, `organisms/` cause redundancy.
- **Goal**: Flatten UI primitives into `shared/ui/`. Modularize state into features. Ensure `shared/` does not import `features/`.

### Backend
- **Current State**: Application logic (e.g., Today queries, draft saving, AI orchestration) lives directly inside large API route files.
- **Goal**: Shift orchestration logic to `services/`. Keep routes thin. 

### Database
- **Current State**: Managed by per-table SQL in `database/`. No Alembic. Seed data and required reference data are mixed.
- **Goal**: Maintain the structure but ensure strict SQLAlchemy ORM parity and separate required reference data.
