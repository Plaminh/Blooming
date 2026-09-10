# Blooming

Blooming is a Windows and Linux desktop daily planner that turns natural-language intentions into realistic Daily Plans, supports Pomodoro execution, repairs unfinished work when reality changes, and reflects lasting progress in one living garden.

Mr. Bloom is a small robot cat and Blooming's visual identity: warm, concise, occasionally enthusiastic, and honest about unrealistic plans. Planning is the product core. The optional Mr. Bloom widget keeps the plan present on the desktop without keeping the full application open.

The frozen product concept is `02-product/Blooming-Concept-Updated.md`.

## Core capabilities

- Planning chat in the full application turns language into a reviewable Task Draft. Mr. Bloom asks only material clarification questions.
- Deterministic scheduling validates availability, deadlines, fixed/flexible Tasks, duration, priority, dependencies, breaks, buffers, edits, and Reality Check (`COMFORTABLE` / `TIGHT` / `OVERLOADED`), returning one ordered PlanBlock timeline.
- Today supports task selection, Pomodoro setup, and FocusRun outcomes `DONE`, `NEED_MORE_TIME`, `SKIP`, and `FINISHED_EARLY`. Planned and actual time stay separate.
- Goals provide an editable Goal → Roadmap → Milestone chain. Reminders ask whether to confirm a Daily Plan; they never auto-create detailed tasks.
- FastAPI stores reminder state. Tauri evaluates due times locally, shows a tray red-dot for unread due reminders, and displays Mr. Bloom's widget bubble. There is no OS toast and no per-second backend polling.
- Heart Progress is permanent visual progress, not currency. One shared GardenState grows through `DORMANT` → `SPROUTING` → `GROWING` → `BLOOMING` → `FLOURISHING`. PlantType (`POTHOS`, `CACTUS`, `BONSAI`, `SUNFLOWER`, `LOTUS`) is visual only; switching it does not reset progress.
- Widget functional states (`DEFAULT`, `REMINDER`, `FOCUSING`, `SESSION_RESULT`, `HIDDEN`) are separate from WidgetContext (time-of-day plus optional WeatherContext). Time and weather never affect scheduling, reminders, or Heart Progress.

## Technology

| Layer | Direction |
|---|---|
| Desktop shell | Tauri 2 / Rust |
| Desktop UI | Svelte + TypeScript + Vite |
| Backend API | Python + FastAPI + Pydantic |
| Persistence | PostgreSQL + SQLAlchemy |
| Authentication | JWT |
| AI | Remote LLM API with validated structured output |
| Weather context | Remote weather API through FastAPI, coarse cache only |
| Deployment | Dockerized backend |

## Status

This documentation describes the frozen MVP concept and intended implementation. It does not claim a completed product. Mobile, web-only, and macOS releases, OS notifications, email/push reminders, shops, inventory, currency, gacha, plant death, multiple gardens, weather-driven planning, and continuous GPS tracking are outside the MVP.

## Documentation

- Product concept (source of truth): `02-product/Blooming-Concept-Updated.md`
- Discovery: `01-discovery/`
- Product: `02-product/`
- Management: `03-management/`
- Requirements: `04-requirements/`
- UI/UX: `05-ui-ux/`
- Architecture: `06-architecture/`
- Specifications: `07-specifications/`
- Testing: `08-testing/`
