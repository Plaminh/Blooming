# ADR-001: Use a Modular Monolith for the MVP

| Field | Value |
|---|---|
| Status | Accepted |
| Date | 8 September 2026 |
| Supersedes/superseded by | None |

## Context and decision drivers

- Blooming is implemented and maintained by one developer.
- Planning, focus, re-planning, and rewards share a domain and transactional data.
- Small evidence-producing increments require low operational and coordination overhead.
- The codebase still needs clear boundaries for testing and portfolio explanation.

## Options considered

| Option | Advantages | Disadvantages |
|---|---|---|
| Layered monolith without modules | Fast initial setup | Feature boundaries erode and unrelated changes become coupled |
| Modular monolith | One deployable unit with explicit domain/application/infrastructure boundaries | Requires discipline; boundaries are not enforced by network isolation |
| Microservices | Independent deployment and scaling | Excessive deployment, data, latency, and testing overhead for one developer/MVP |

## Decision

Blooming will use a modular monolith: one Spring Boot deployable API organized by product modules such as planning, focus, and reward. Each module separates API, application, domain, and infrastructure concerns where useful.

## Consequences

- Positive: simple deployment and transactions while retaining explainable module boundaries.
- Positive: domain logic can be tested without web/database/AI infrastructure.
- Tradeoff: module boundaries require architecture tests and code review rather than network enforcement.
- Follow-up: avoid creating empty future modules; add a module only when its feature enters implementation.

## Reconsider when

A measured scaling, ownership, security, or deployment requirement cannot be met reasonably within one deployable application.

## Stack update: 9 September 2026

The backend now uses FastAPI/Python, with PostgreSQL, SQLAlchemy, and Alembic
as the persistence direction. The original decision above retains its historical
framework wording; the accepted modular-monolith boundaries remain unchanged.
Only the FastAPI skeleton and health endpoint are currently implemented.
