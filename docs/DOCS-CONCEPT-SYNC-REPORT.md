# Documentation Sync Report

## Source of Truth

- `docs/02-product/Blooming-Concept-Updated.md`

## Files Modified

### Product and discovery

| Path | Major changes |
|---|---|
| `docs/02-product/Blooming-Concept-Updated.md` | In-repo frozen concept. WidgetState vs WidgetContext, `SESSION_RESULT` outcomes including `FINISHED_EARLY → DEFAULT` without automatic re-planning, weather-disabled vs `UNKNOWN`, Heart Progress / GardenState wording, and PlanningSession/PlanningMessage as runtime/domain concepts that do not require storing raw chat. |
| `docs/project-readme.md` | Desktop stack, widget/plant/reminder model, and out-of-scope list aligned to the concept. |
| `docs/02-product/mvp-scope.md` | MVP blocks include widget, PlantType, Heart Progress/GardenState, and presentation-only weather. |
| `docs/02-product/vision-document.md` | Desktop positioning; WidgetState independent from WidgetContext; FastAPI/Tauri reminders; weather presentation-only. |
| `docs/01-discovery/product-proposal.md` | Desktop planner proposal; removed web/mobile framing and garden-economy ideas. |
| `docs/01-discovery/app-survey.md` | Plant comparison updated to one GardenState plus visual PlantType. |
| `docs/README.md` | Concept declared as source of truth; `## Added for Blooming` restored as a heading. |
| `docs/CHANGELOG.md` | Records concept alignment. |

### Requirements

| Path | Major changes |
|---|---|
| `docs/04-requirements/domain-rules.md` | Heart Progress, GardenState, PlantType, WidgetState, WidgetContext (visual only), WeatherContext; Milestone ReminderAction vs focus/task actions; weather-disabled ≠ `UNKNOWN`; PlanningSession/PlanningMessage as runtime/domain; scheduler BR-021–037 preserved. |
| `docs/04-requirements/functional-requirements.md` | Desktop settings, independent WidgetState/WidgetContext, `SESSION_RESULT` outcomes including `FINISHED_EARLY → DEFAULT` without automatic re-planning, plant switch, WeatherSnapshot cardinality. |
| `docs/04-requirements/non-functional-requirements.md` | Desktop targets; reminder/weather/plant NFRs; fetch-`UNKNOWN` vs disabled overlay. |
| `docs/04-requirements/use-case-model.md` | Widget, plant-switch, and weather-presentation use cases; UC-PLAN-01 labeled Create Daily Plan. |
| `docs/04-requirements/use-cases/uc-plan-01-create-quick-plan.md` | Trigger from Today; title aligned to Daily Plan; filename retained. |
| `docs/04-requirements/use-cases/uc-plan-02-handle-overload.md` | Extends Daily Planning (UC-PLAN-01). |

### UI, architecture, and ADRs

| Path | Major changes |
|---|---|
| `docs/05-ui-ux/ui-ux-design.md` | Screens are Today, Goals, Settings; widget states are not screens; `SESSION_RESULT` is where outcomes are chosen, including `FINISHED_EARLY → DEFAULT` without automatic re-planning; WidgetContext is visual only; Task Draft / Daily Planning labels; reminder action sets kept distinct. |
| `docs/06-architecture/system-context.md` | Tauri + Svelte + FastAPI + PostgreSQL; weather provider; at most one WeatherSnapshot; Daily Planning wording. |
| `docs/06-architecture/container-component.md` | Desktop container, local reminder/timer evaluation, garden/weather modules; one current WeatherSnapshot cache. |
| `docs/06-architecture/data-api-design.md` | HeartEvent, GardenState, PlantType, replaceable WeatherSnapshot (at most one current cache per user); ReminderAction distinction; WidgetState runtime vs WidgetContext; PlanningSession/PlanningMessage removed from persisted names and ER (runtime/domain only; no raw chat transcript). |
| `docs/06-architecture/security-privacy.md` | Desktop trust boundary; city/coarse location without GPS history; raw conversational planning text not durably persisted by default. |
| `docs/06-architecture/adr/adr-001-modular-monolith.md` | One FastAPI deployable plus a Tauri shell. |
| `docs/06-architecture/adr/adr-004-time-and-timezone-strategy.md` | Local WidgetContext time-of-day is presentation-only. |

### Management, specifications, testing, frontend docs

| Path | Major changes |
|---|---|
| `docs/03-management/project-plan.md` | Widget countdown, desktop reminders, PlantType, weather fallback. |
| `docs/03-management/product-backlog.md` | Settings, reminder, and garden items match the concept. |
| `docs/07-specifications/001-quick-planning/spec.md` | Domain increment for a desktop product; folder name retained. |
| `docs/07-specifications/001-quick-planning/plan.md` | Scheduler domain is Python. |
| `docs/07-specifications/001-quick-planning/tasks.md` | Python alignment; garden/widget/weather remain out of this increment. |
| `docs/08-testing/test-plan.md` | Desktop/E2E, reminder sync, plant-switch, disabled vs `UNKNOWN` weather gates. |
| `docs/08-testing/test-cases-mvp.md` | HeartEvent, PlantType switch, WidgetState, `SESSION_RESULT` outcomes including `FINISHED_EARLY` without automatic re-planning, TC-WIDGET-002 / TC-WIDGET-002b. |
| `frontend/README.md` | Tauri/Svelte product frontend; relative concept path `../docs/02-product/Blooming-Concept-Updated.md`. |
| `frontend/AGENTS.md` | Same relative concept path; leftover Next.js scaffold is not architecture. |
| `docs/DOCS-CONCEPT-SYNC-REPORT.md` | This report. |

Scheduler algorithms, `FOCUS` / `BREAK` / `FIXED_EVENT`, and `DEADLINE_EXCEEDED` as an unscheduled reason are unchanged. ADR-002 and ADR-003 were already consistent.

## Outdated Concepts Removed

- Next.js/React product frontend
- Spring Boot/Java backend
- browser/mobile MVP
- Water Reserve
- Rest Mode
- PlantState health/death system
- email reminder MVP
- OS toast notifications
- multiple plant progress tracks
- inventory/shop/currency/gacha
- weather-driven planning
- WidgetContext containing WidgetState
- weather-disabled requiring WeatherContext `UNKNOWN`
- outcome selection before `SESSION_RESULT`
- durable raw conversational chat history implied by PlanningSession/PlanningMessage
- Home / Mr. Bloom as a primary application screen
- user-facing Quick Plan as a separate product surface (historical spec folder `001-quick-planning/` retained)

## New Concepts Propagated

- Tauri 2 + Svelte desktop frontend
- FastAPI backend
- WidgetState
- WidgetContext
- WeatherContext
- WeatherSnapshot
- time-only weather fallback
- Heart Progress
- HeartEvent
- GardenState
- PlantType
- five plant types (`POTHOS`, `CACTUS`, `BONSAI`, `SUNFLOWER`, `LOTUS`)
- compositional widget visuals (WidgetState + WidgetContext + PlantType/GardenState)
- Tauri local timer/reminder evaluation
- tray red-dot reminder presentation
- PlanningSession / PlanningMessage as runtime/domain concepts without durable raw chat
- `FINISHED_EARLY → DEFAULT` without automatic re-planning

## Remaining Ambiguities

- Exact local-hour cutovers for `MORNING`, `AFTERNOON`, `EVENING`, and `NIGHT`.
- Numeric Heart Progress amounts and GardenState stage thresholds.
- Weather provider choice and mapping from provider condition codes to WeatherContext.

## Consistency Check

| Area | Result |
|---|---|
| Technology stack | **Consistent:** Tauri 2 / Rust, Svelte + TypeScript + Vite, FastAPI + Python, PostgreSQL + SQLAlchemy, remote LLM, JWT. Next.js/React mentions exist only as leftover-scaffold warnings in `frontend/`. |
| Windows/Linux platform scope | **Consistent.** Mobile, web-only, and macOS remain out of MVP. |
| Full-app vs widget boundary | **Consistent:** Today, Goals, Settings plus optional widget. Planning chat is full-app only. |
| WidgetState vs WidgetContext separation | **Consistent:** WidgetState is functional; WidgetContext is time-of-day plus optional WeatherContext and does not contain WidgetState. Rendered widget = WidgetState + WidgetContext + PlantType/GardenState. |
| Plant model | **Consistent:** one GardenState, selectable PlantType, no inventory/shop/death in MVP, `FLOURISHING` included. |
| Heart Progress terminology | **Consistent:** Heart Progress for the visual ledger; HeartEvent for auditable records. Informal “Heart rewards” wording was removed from the concept. |
| Weather behavior | **Consistent:** presentation-only; disabled visuals omit overlay without requiring `UNKNOWN`; fetch failure may use `UNKNOWN`; neither affects scheduling, reminders, Heart Progress, or planning. At most one current WeatherSnapshot per user. |
| Reminder architecture | **Consistent:** FastAPI stores definitions/state; Tauri evaluates due times locally; tray red-dot + widget bubble; no per-second polling; no OS toast. Milestone ReminderAction values are distinct from `START_FOCUS` / `OPEN_BLOOMING`. |
| AI/application boundary | **Consistent:** LLM interprets in the full application; deterministic code schedules, times, persists, and owns Heart Progress / reminder execution. Raw conversational planning text is not durably persisted by default. |
| MVP vs post-MVP boundary | **Consistent** with the concept, including Vitality as post-MVP. |

### Final repository audit

Markdown documentation was searched for Next.js, React, Spring Boot, Java, JPA, Hibernate, Water Reserve, Rest Mode, PlantState, MeaningfulActivity, RewardEvent, RestPeriod, CREATE_TOMORROWS_PLAN, FRUITING, SEED, SPROUT, YOUNG, MATURE, HEALTHY, DRY, WILTING, CRITICAL, DEAD, email reminder, mobile browser, and Home / Mr. Bloom.

Allowed remaining hits:

- `frontend/README.md` and `frontend/AGENTS.md` describe leftover Next.js/React scaffolding as non-canonical.
- `docs/05-ui-ux/ui-ux-design.md` states that there is no Water Reserve meter.

No other documentation hits required a product-doc rewrite. Repo-root `a.txt` is a leftover git diff dump, not documentation, and was left unchanged.
