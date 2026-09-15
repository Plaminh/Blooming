# Tasks: Statistics Screen

**Input**: Design documents from `/specs/010-statistics-screen/`

**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, quickstart.md

**Tests**: Tests are required per the Constitution (Principle 6) and spec (SC-003, SC-011). Each user story has independently verifiable acceptance criteria.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app (desktop frontend)**: `frontend/src/` at repository root
- Feature code: `frontend/src/lib/features/statistics/`
- Shared code: `frontend/src/lib/shared/components/`
- Route: `frontend/src/routes/statistics/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create feature module structure, types, and mock data

- [x] T001 Create Statistics feature types in `frontend/src/lib/features/statistics/types.ts` — define `StatisticsDateRange`, `SummaryMetrics`, `CalendarDayState`, `StudyStatus`, `CalendarMonth`, `DailyStudyEntry`, `PlanHistoryEntry`, `PlanStatus`, `HistoryFilter`, `PaginationState` per data-model.md
- [x] T002 Create mock data fixtures in `frontend/src/lib/features/statistics/data/mockData.ts` — define typed constants for all date ranges, summary metrics, calendar studied days (June 2026: days 1–9, 11, 12, 14), daily study entries (Mon 2h, Tue 3h, Wed 0h, Thu 2.5h, Fri 4h, Sat 0h, Sun 3h), and 11 plan history entries (first page: Jun 14/Learn machine learning/3÷3/Completed, Jun 12/Build backend API/2÷3/Unfinished, Jun 11/Study databases/3÷3/Completed, Jun 9/Refine Blooming UI/1÷3/Unfinished)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Modify shared components so the Statistics route and sidebar item are recognized by the application shell

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Add `'statistics'` to `IconName` type union and add SVG path (three ascending vertical bars using `currentColor`, `fill="currentColor" stroke="none"`) in `frontend/src/lib/shared/components/atoms/AppIcon.svelte`
- [x] T004 Add `'statistics'` to the `icon` prop union type in `frontend/src/lib/shared/components/molecules/SidebarNavigationItem.svelte` — change `icon: 'today' | 'goals' | 'chat' | 'settings'` to include `| 'statistics'`
- [x] T005 Add `'STATISTICS'` to the `activeRoute` union type in `frontend/src/lib/shared/components/organisms/DesktopAppShell.svelte` — change `activeRoute?: 'TODAY' | 'GOALS' | 'MR. BLOOM' | 'SETTINGS'` to include `| 'STATISTICS'`
- [x] T006 Add STATISTICS navigation item in `frontend/src/lib/shared/components/organisms/AppSidebar.svelte` — insert `<SidebarNavigationItem label="STATISTICS" icon="statistics" active={activeRoute === 'STATISTICS'} onClick={() => goto('/statistics')} />` between the MR. BLOOM and SETTINGS items

**Checkpoint**: Foundation ready — shared components accept the Statistics route and icon. All existing pages remain unchanged.

---

## Phase 3: User Story 5 — Navigate to Statistics via Shared Sidebar (Priority: P1) 🎯 MVP

**Goal**: Users can see and click the STATISTICS sidebar entry from any page to navigate to `/statistics` with the correct active state.

**Independent Test**: Navigate to `/statistics` from any existing page by clicking the sidebar item. Verify the sidebar shows STATISTICS between MR. BLOOM and SETTINGS with a bar-chart icon, and the active state displays correctly.

### Implementation for User Story 5

- [x] T007 [US5] Create route page `frontend/src/routes/statistics/+page.svelte` — import `DesktopAppShell` with `activeRoute="STATISTICS"`, render a placeholder heading "STATISTICS" inside the shell. This validates sidebar navigation end-to-end before other stories add content.

**Checkpoint**: At this point, the STATISTICS sidebar item is visible on all pages and navigates to `/statistics`. The page renders inside the app shell with the correct active state. Keyboard navigation (Tab + Enter) and `aria-current="page"` work via the existing `SidebarNavigationItem` implementation.

---

## Phase 4: User Story 1 — View Study Progress Summary (Priority: P1)

**Goal**: Users see a page header with the "STATISTICS" title, subtitle, date-range selector, and three summary KPI cards showing study time, study days, and plan counts.

**Independent Test**: Navigate to `/statistics` and verify the heading, subtitle, date-range selector text, and all three summary cards render with correct icons, labels, and formatted values.

### Implementation for User Story 1

- [x] T008 [P] [US1] Create `SummaryCard` atom in `frontend/src/lib/features/statistics/components/atoms/SummaryCard.svelte` — renders one KPI card with `AppIcon` (via `iconName` prop), uppercase label, and large bold value. Styled with white background, subtle border (`--bloom-border-subtle`), border-radius 8px, internal padding. Props: `iconName: IconName`, `label: string`, `value: Snippet` (use Svelte Snippet for flexible value rendering like "8 complete / 3 unfinished")
- [x] T009 [P] [US1] Create `DateRangeSelector` molecule in `frontend/src/lib/features/statistics/components/molecules/DateRangeSelector.svelte` — rounded button showing calendar `AppIcon` + `displayLabel` text + dropdown chevron SVG. On click, toggles an absolutely-positioned `<ul>` dropdown of options. Click outside closes. Props: `ranges: StatisticsDateRange[]`, `selectedRange: StatisticsDateRange`, `onSelect: (range: StatisticsDateRange) => void`. Add `aria-expanded`, `aria-haspopup="listbox"`, and keyboard support (Escape to close)
- [x] T010 [US1] Create `StatisticsHeader` organism in `frontend/src/lib/features/statistics/components/organisms/StatisticsHeader.svelte` — flexbox row. Left side: `<h1>` "STATISTICS" in `--bloom-display-font` (~28px, `--bloom-text-dark-blue`), `<p>` subtitle "Your progress, one day at a time." in `--bloom-body-font` (~14px, `--bloom-text-muted-blue`). Right side: `DateRangeSelector`. Props: `ranges`, `selectedRange`, `onRangeChange`
- [x] T011 [US1] Create `SummaryCardRow` organism in `frontend/src/lib/features/statistics/components/organisms/SummaryCardRow.svelte` — horizontal flex row with gap 16px containing three `SummaryCard` instances: (1) clock icon / "STUDY TIME" / "24h 30m", (2) calendar icon / "STUDY DAYS" / "10 days", (3) document icon / "PLANS" / "8 complete / 3 unfinished". Props: `metrics: SummaryMetrics`
- [x] T012 [US1] Integrate `StatisticsHeader` and `SummaryCardRow` into `frontend/src/routes/statistics/+page.svelte` — replace placeholder with full layout. Import mock data. Add `$state` for `selectedRange`. Render header and summary cards. Wrap content in a scrollable container with padding `20px 24px`

**Checkpoint**: Statistics page displays heading, subtitle, date-range selector, and three summary KPI cards matching the reference layout.

---

## Phase 5: User Story 2 — Review Study Calendar (Priority: P1)

**Goal**: Users see a month calendar for June 2026 with green-highlighted study days, neutral non-study days, month navigation, and a legend.

**Independent Test**: Verify the calendar renders June 2026 with correct day states (days 1–9, 11, 12, 14 green). Click next/prev month buttons and verify the month label and grid update. Verify the legend is visible.

### Implementation for User Story 2

- [x] T013 [P] [US2] Create `CalendarDayCell` atom in `frontend/src/lib/features/statistics/components/atoms/CalendarDayCell.svelte` — renders a single day number in a grid cell. Props: `day: number`, `state: 'studied' | 'no-record' | 'inactive' | 'empty'`. Studied: green background (`#C8F0D0`), dark text. No-record: white background. Inactive (future): pale gray-blue (`#EBF2F6`), muted text. Empty: invisible placeholder for grid offset. Fixed cell size for uniform grid
- [x] T014 [P] [US2] Create `CalendarMonthNav` molecule in `frontend/src/lib/features/statistics/components/molecules/CalendarMonthNav.svelte` — centered month label (e.g., "June 2026") flanked by `<` and `>` buttons. Buttons: rounded border, compact sizing, `aria-label="Previous month"` / `"Next month"`. Props: `monthLabel: string`, `onPrev: () => void`, `onNext: () => void`
- [x] T015 [P] [US2] Create `CalendarLegend` molecule in `frontend/src/lib/features/statistics/components/molecules/CalendarLegend.svelte` — horizontal flex with two items: green square + "Studied", gray square + "No record". Uses CSS `::before` or inline `<span>` for color swatches
- [x] T016 [US2] Create `StudyCalendarPanel` organism in `frontend/src/lib/features/statistics/components/organisms/StudyCalendarPanel.svelte` — white panel with `<h2>` "STUDY CALENDAR", `CalendarMonthNav`, weekday header row (Mon–Sun), 7-column CSS Grid of `CalendarDayCell` components, and `CalendarLegend`. Internal `$state` for `currentYear` and `currentMonth` (default: 2026, 5 for June). Compute `daysInMonth` via `new Date(year, month + 1, 0).getDate()` and `firstWeekdayOffset` via `(new Date(year, month, 1).getDay() + 6) % 7`. Generate empty cells for offset, day cells with studied/no-record state from mock data, and inactive cells for future days. Props: `studiedDays: CalendarDayState[]` (or load from mock data internally). Panel has fixed dimensions so it doesn't resize on month change
- [x] T017 [US2] Add `StudyCalendarPanel` to `frontend/src/routes/statistics/+page.svelte` — add a two-column CSS Grid row below the summary cards (columns: `~54% ~46%` or `minmax(0,1fr) minmax(0,1fr)` with gap 16px). Place `StudyCalendarPanel` in the left column. Right column placeholder for chart (Phase 6)

**Checkpoint**: Calendar renders June 2026 with correct studied days. Month navigation works. Panel size stable. Legend visible.

---

## Phase 6: User Story 3 — Review Daily Study Time Chart (Priority: P1)

**Goal**: Users see a vertical bar chart showing daily study hours for the week Jun 8–14, with value labels, weekday labels, and zero-day baseline markers.

**Independent Test**: Verify 7 bars render with correct value labels (2h, 3h, 0h, 2.5h, 4h, 0h, 3h). Verify zero-hour days show a baseline marker. Verify Fri (4h) is the tallest bar. Verify accessible labels exist.

### Implementation for User Story 3

- [x] T018 [P] [US3] Create `BarChartColumn` atom in `frontend/src/lib/features/statistics/components/atoms/BarChartColumn.svelte` — renders a single vertical bar in the chart. Uses CSS flexbox with `flex-direction: column`, `align-items: center`, `justify-content: flex-end`. Bar `<div>` has green background (`--bloom-primary-green` or `#45A26B`), width ~40px, height as percentage of `maxHours` prop (e.g., `height: ${(hours / maxHours) * 100}%`). Value label `<span>` positioned above bar. Weekday label `<span>` below baseline. Zero-value: bar height 0, show a 3px neutral gray baseline marker. `aria-label` on the container: e.g., "Monday: 2 hours". Props: `dayLabel: string`, `hours: number`, `maxHours: number`
- [x] T019 [US3] Create `DailyStudyTimeChart` organism in `frontend/src/lib/features/statistics/components/organisms/DailyStudyTimeChart.svelte` — white panel with `<h2>` "DAILY STUDY TIME", subtitle `<p>` (e.g., "Jun 8 - 14"), and a flex row of 7 `BarChartColumn` instances with `justify-content: space-around`. Compute `maxHours` as `Math.max(...entries.map(e => e.hours))` (floor at 1 to avoid division by zero). Chart area has a fixed min-height (~200px) so bars have room. Props: `entries: DailyStudyEntry[]`, `subtitle: string`
- [x] T020 [US3] Add `DailyStudyTimeChart` to `frontend/src/routes/statistics/+page.svelte` — place in the right column of the two-column grid row (replacing placeholder from T017). Import daily study mock data and pass as props

**Checkpoint**: Bar chart renders 7 days with correct proportions. Zero-day markers visible. Chart sits beside the calendar panel.

---

## Phase 7: User Story 4 — Browse and Filter Plan History (Priority: P2)

**Goal**: Users see a plan history table with date, plan, tasks, status columns, filter buttons (All/Completed/Unfinished), pagination controls, and row chevrons.

**Independent Test**: Verify the table renders 4 reference rows. Click each filter and verify correct rows appear. Navigate through pages. Verify disabled state at pagination boundaries. Verify "Showing 4 of 11 plans" and "1 / 3" indicator.

### Implementation for User Story 4

- [x] T021 [P] [US4] Create `FilterButton` atom in `frontend/src/lib/features/statistics/components/atoms/FilterButton.svelte` — pill-shaped `<button>` with rounded border. Active state: light-blue background (`#CBE7FF`), dark text. Inactive: white/transparent background, border visible. Props: `label: string`, `active: boolean`, `onClick: () => void`. Focus-visible: outline `2px solid #008ec5`
- [x] T022 [P] [US4] Create `StatusBadge` atom in `frontend/src/lib/features/statistics/components/atoms/StatusBadge.svelte` — pill badge with icon + text. Completed: green background (`#DDF7E4`), green check-circle icon (use `AppIcon` name `check_circle` or inline SVG filled circle-check), dark green text. Unfinished: gray background (`#EBF1F5`), open circle icon (inline SVG), slate text. Props: `status: PlanStatus`. Status communicated by distinct icon shape + text label (not color alone, per FR-036)
- [x] T023 [P] [US4] Create `PlanHistoryRow` molecule in `frontend/src/lib/features/statistics/components/molecules/PlanHistoryRow.svelte` — renders a `<tr>` with `<td>` cells for date, plan name, tasks (e.g., "3 / 3"), `StatusBadge`, and a clickable chevron button (`AppIcon` name `chevron-right`). Props: `entry: PlanHistoryEntry`, `onNavigate: (id: string) => void`. Chevron button has `aria-label="View plan details"`, `tabindex="0"`, and keyboard activation
- [x] T024 [P] [US4] Create `PaginationControls` molecule in `frontend/src/lib/features/statistics/components/molecules/PaginationControls.svelte` — flex row with previous button (`<`), page indicator text ("1 / 3"), next button (`>`). Previous disabled when `currentPage === 1`. Next disabled when `currentPage === totalPages`. Buttons have `aria-label="Previous page"` / `"Next page"`. Props: `currentPage: number`, `totalPages: number`, `onPageChange: (page: number) => void`
- [x] T025 [US4] Create `PlanHistoryPanel` organism in `frontend/src/lib/features/statistics/components/organisms/PlanHistoryPanel.svelte` — white panel with `<h2>` "PLAN HISTORY", filter buttons row (All/Completed/Unfinished using `FilterButton`), `<table>` with `<thead>` (`<th>` for DATE, PLAN, TASKS, STATUS), `<tbody>` rendering `PlanHistoryRow` for visible entries, and footer with "Showing X of Y plans" text and `PaginationControls`. Internal `$state`: `activeFilter: HistoryFilter` (default 'All'), `currentPage: number` (default 1). `$derived`: `filteredEntries` (filter by status), `totalPages`, `visibleEntries` (paginated slice), `showingCount`. Reset `currentPage` to 1 when filter changes. Props: `entries: PlanHistoryEntry[]`, `itemsPerPage: number` (default 4). Empty state: when filtered results are empty, show "No plans found" message in table body
- [x] T026 [US4] Add `PlanHistoryPanel` to `frontend/src/routes/statistics/+page.svelte` — add below the calendar/chart row as a full-width section. Import plan history mock data (all 11 entries) and pass with `itemsPerPage={4}`

**Checkpoint**: Plan history table renders correctly. Filters work (only one active at a time). Pagination navigates between pages. Status badges show distinct icons. All controls keyboard accessible.

---

## Phase 8: User Story 6 — Change Date Range (Priority: P3)

**Goal**: Users can change the reporting date range using the dropdown selector. Summary cards, calendar, and chart update to reflect the selected range.

**Independent Test**: Open the date-range dropdown, select a different range, and verify the summary card values, calendar studied days, and chart data update.

### Implementation for User Story 6

- [x] T027 [US6] Add multiple date-range mock datasets in `frontend/src/lib/features/statistics/data/mockData.ts` — create at least 2 additional `StatisticsDateRange` options with corresponding `SummaryMetrics`, `CalendarDayState[]`, and `DailyStudyEntry[]` data. Export a lookup function or map: `(rangeId: string) => { metrics, calendarDays, dailyEntries, planEntries }`
- [x] T028 [US6] Wire date-range selection in `frontend/src/routes/statistics/+page.svelte` — when `selectedRange` changes via `DateRangeSelector.onSelect`, update the `$derived` data flowing to `SummaryCardRow`, `StudyCalendarPanel`, and `DailyStudyTimeChart` by looking up the selected range's corresponding mock data

**Checkpoint**: Changing the date range updates all dependent panels with new data.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Tests, accessibility audit, visual verification, and regression checking

- [x] T029 [P] Create feature tests in `frontend/src/lib/features/statistics/StatisticsView.test.ts` — test cases: (1) Statistics page renders heading "STATISTICS" and subtitle, (2) three summary cards display correct labels and values, (3) sidebar shows STATISTICS between MR. BLOOM and SETTINGS, (4) calendar renders June 2026 with correct studied days, (5) month navigation changes month label, (6) bar chart renders 7 bars with correct value labels, (7) plan history table displays 4 rows with correct data, (8) filter buttons toggle correctly and show correct rows, (9) pagination navigates between pages with correct disabled states, (10) `aria-current="page"` set on active sidebar item. Use `render`, `screen`, `fireEvent` from `@testing-library/svelte`
- [x] T030 [P] Accessibility audit on `frontend/src/routes/statistics/+page.svelte` — verify: `<h1>` for "STATISTICS", `<h2>` for all panel titles, `<table>` with `<th>` headers, `aria-label` on all interactive elements (filter buttons, pagination buttons, month nav buttons, row chevrons, date-range selector, bar chart columns), visible focus rings on all interactive elements, `prefers-reduced-motion` respected (already handled in global CSS), status indicators use icon shape + text (not color alone)
- [x] T031 Run `npm run check` from `frontend/` — verify no TypeScript errors after all changes
- [x] T032 Run `npm run test` from `frontend/` — verify all existing and new tests pass
- [x] T033 Visual verification — launch with `npm run tauri dev`, navigate to `/statistics`, compare side-by-side with `design-assets/app/references/statistic.png`. Verify layout, typography, colors, spacing, borders, icons, bar proportions, calendar states, table alignment, status badges. Verify no content overflow at 1280×800. Verify no console errors
- [x] T034 Regression check — navigate to Today, Goals, Mr. Bloom, Settings pages and verify they render correctly with the STATISTICS sidebar item present. Verify no console errors on any page

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 (types needed for mock data, but T003–T006 only modify shared components) — BLOCKS all user stories
- **US5 — Sidebar Navigation (Phase 3)**: Depends on Phase 2. Creates the route. Should be done first as all other stories add content to this page
- **US1 — Summary (Phase 4)**: Depends on Phase 3 (page exists)
- **US2 — Calendar (Phase 5)**: Depends on Phase 3 (page exists). Can parallel with US1
- **US3 — Chart (Phase 6)**: Depends on Phase 5 (shares the two-column grid row with calendar — T017 creates the grid)
- **US4 — Plan History (Phase 7)**: Depends on Phase 3 (page exists). Can parallel with US1, US2
- **US6 — Date Range (Phase 8)**: Depends on US1 (header/selector), US2 (calendar), US3 (chart). Must be last content story
- **Polish (Phase 9)**: Depends on all user stories being complete

### User Story Dependencies

```
Phase 1 (Setup) → Phase 2 (Foundation) → Phase 3 (US5: Route)
                                              │
                          ┌───────────────────┼───────────────────┐
                          ▼                   ▼                   ▼
                   Phase 4 (US1)       Phase 5 (US2)       Phase 7 (US4)
                          │                   │
                          │                   ▼
                          │            Phase 6 (US3)
                          │                   │
                          └─────────┬─────────┘
                                    ▼
                             Phase 8 (US6)
                                    │
                                    ▼
                             Phase 9 (Polish)
```

### Within Each User Story

- Atoms ([P] tasks) before molecules
- Molecules before organisms
- Organisms before page integration
- Page integration completes the story

### Parallel Opportunities

- T001 and T002 can run in parallel (types and mock data are independent files)
- T003, T004, T005, T006 can run in parallel (different shared component files)
- Within US1: T008 and T009 can run in parallel (SummaryCard atom and DateRangeSelector molecule)
- Within US2: T013, T014, T015 can run in parallel (CalendarDayCell, CalendarMonthNav, CalendarLegend)
- Within US4: T021, T022, T023, T024 can run in parallel (FilterButton, StatusBadge, PlanHistoryRow, PaginationControls)
- US1 (Phase 4), US2 (Phase 5), and US4 (Phase 7) can run in parallel after Phase 3
- T029 and T030 can run in parallel (test file and accessibility audit)

---

## Parallel Example: User Story 4 (Plan History)

```bash
# Launch all atoms/molecules in parallel (different files):
Task: "Create FilterButton atom in frontend/src/lib/features/statistics/components/atoms/FilterButton.svelte"
Task: "Create StatusBadge atom in frontend/src/lib/features/statistics/components/atoms/StatusBadge.svelte"
Task: "Create PlanHistoryRow molecule in frontend/src/lib/features/statistics/components/molecules/PlanHistoryRow.svelte"
Task: "Create PaginationControls molecule in frontend/src/lib/features/statistics/components/molecules/PaginationControls.svelte"

# Then sequentially:
Task: "Create PlanHistoryPanel organism" (depends on above)
Task: "Integrate into page" (depends on organism)
```

---

## Implementation Strategy

### MVP First (US5 + US1 Only)

1. Complete Phase 1: Setup (types + mock data)
2. Complete Phase 2: Foundational (shared component modifications)
3. Complete Phase 3: US5 (route + sidebar integration)
4. Complete Phase 4: US1 (header + summary cards)
5. **STOP and VALIDATE**: Page renders with heading, date selector, and 3 KPI cards
6. Run `npm run check` and `npm run test`

### Incremental Delivery

1. Setup + Foundation → Route exists, sidebar works
2. Add US5 + US1 → Header + summary cards (MVP!)
3. Add US2 → Calendar panel renders in left column
4. Add US3 → Chart panel renders in right column
5. Add US4 → Plan history table with filters + pagination
6. Add US6 → Date range selector updates all panels
7. Polish → Tests, accessibility, visual verification, regression check
8. Each story adds visual content without breaking previous stories

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit only when explicitly authorized; when authorized, group commits by completed task or logical unit
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
- The `SidebarNavigationItem` already implements `aria-current="page"` and focus-visible styling — no extra work needed for keyboard accessibility of the sidebar item
- The global CSS already handles `prefers-reduced-motion` — no extra work needed (FR-038)
- No contracts/ directory generated — this feature has no external interfaces
