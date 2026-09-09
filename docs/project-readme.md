# Blooming

Blooming is an adaptive conversational personal planner that turns natural-language daily intentions and long-term goals into realistic plans, guides focus sessions, recovers unfinished schedules when reality changes, connects milestones to future Daily Plans through reminders, and represents sustained progress through one living plant.

Mr. Bloom is an old AI robot and the central conversational guide. Mature, calm, practical, and concise, he challenges unrealistic plans, supports recovery without excessive enthusiasm, and remains non-judgmental when the user falls behind. His distant-future mission to help restore plant life supplies atmosphere without becoming a pet, quest, campaign, or multi-agent system.

## Core capabilities

- Mr. Bloom turns language into reviewable Task Drafts and Roadmap Drafts, asks only material clarification questions, and explains realistic recovery choices.
- Deterministic scheduling validates availability, deadlines, fixed/flexible Tasks, non-Task fixed events, duration, priority, dependencies, precise breaks, buffers, edits, and `COMFORTABLE`/`TIGHT`/`OVERLOADED` status, returning one ordered PlanBlock timeline.
- Today supports focus countdown, pause/resume, `DONE`, `FINISHED_EARLY`, `NEED_MORE_TIME`, and `SKIP`, with planned and actual time kept separate.
- Goals provide editable milestones and local-time in-app/basic email reminders that can start tomorrow's plan after confirmation.
- One backend-owned plant uses growth/health states, Water Reserve, meaningful activity, and Rest Mode. Missed work is recoverable, not punishment.

## Technology

| Layer | Direction |
|---|---|
| Frontend | Next.js, React, TypeScript |
| Backend | Python, FastAPI modular monolith |
| Persistence | PostgreSQL with SQLAlchemy; Alembic migrations |
| Authentication | JWT |
| AI | Direct LLM API integration with validated structured output |
| Email/deployment | Scheduled Python service (planned), one email provider, Docker |

## Status

The backend currently provides a FastAPI skeleton with a health endpoint; product features remain unimplemented. This documentation does not claim a deployed application or completed features. Google Calendar, analytics, learned estimates, teams/social features, multiple plants/economy, pet/world systems, complex web push, multiple agents, LangChain, and LangGraph are outside the MVP.

## Documentation

- Discovery: `01-discovery/`
- Product: `02-product/`
- Management: `03-management/`
- Requirements: `04-requirements/`
- UI/UX: `05-ui-ux/`
- Architecture: `06-architecture/`
- Specifications: `07-specifications/`
- Testing: `08-testing/`
