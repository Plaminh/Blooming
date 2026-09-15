# Implementation Plan: Statistics Screen

**Branch**: `010-statistics-screen` | **Date**: 2026-09-15 | **Spec**: [spec.md](./spec.md)

## Summary

Implement the Blooming Statistics screen matching the `statistic.png` design reference. The screen comprises a page header with date-range selector, three summary KPI cards, a study calendar with month navigation, a daily study time bar chart (CSS-only, no charting library), and a plan history table with filters and pagination. All data uses typed local view-model fixtures. Integration into the shared application shell requires adding a `STATISTICS` sidebar item (with a new `statistics` icon variant on `AppIcon`) between `MR. BLOOM` and `SETTINGS`, and creating the `/statistics` route.

## Technical Context

**Language/Version**: TypeScript 5, Svelte 5 (runes), SvelteKit 2
**Primary Dependencies**: SvelteKit 2, Vite, Tauri 2
**Storage**: Local in-component state (`$state`, `$derived`) for mock data
**Testing**: Vitest + @testing-library/svelte
**Target Platform**: Desktop (Windows/Linux via Tauri), 1280×800 canvas
**Project Type**: Desktop application frontend
**Performance Goals**: Instant UI updates for local view-model interactions
**Constraints**: No third-party charting library; no real backend; no data persistence; fits within 1280×800 without body scrolling
**Scale/Scope**: One new route, one new feature module, ~15 new components, modifications to 2 shared components

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] Does the plan align with the Spec-driven development workflow?
- [x] Does the plan preserve the approved Tauri 2/Rust, SvelteKit/TypeScript/Vite boundaries?
- [x] Does deterministic application code remain authoritative while AI output and external input are validated at trust boundaries?
- [x] Are explicit contracts and type safety boundaries defined?
- [x] Is the proposed implementation the simplest that satisfies the spec?
- [x] Are testable behavior and quality gates defined?
- [x] Does the UX handle loading, partial, and failure states gracefully?
- [x] Are resource efficiency and platform scope strictly followed?
- [x] Are security and privacy principles respected?

### Constitution Alignment Notes

- **Principle 2 (Deterministic ownership)**: All data displayed is from typed local fixtures, clearly identified as non-production mock data. No AI output involved.
- **Principle 3 (Architectural boundaries)**: Changes are purely frontend (SvelteKit/TypeScript). No backend or Rust modifications.
- **Principle 4 (Type safety)**: All entities (`StatisticsDateRange`, `SummaryMetrics`, `CalendarDayState`, `DailyStudyEntry`, `PlanHistoryEntry`, `PaginationState`, `HistoryFilter`) are explicitly typed. See [data-model.md](./data-model.md).
- **Principle 5 (Simple implementation)**: No speculative stores, services, or abstractions. State is co-located in components using `$state`/`$derived`. One feature module with feature-specific components only.
- **Principle 7 (Recoverable UX)**: Empty states defined for zero-study months, zero-hour chart days, empty filter results, and single-page pagination.

## Repository Preflight

- **Current SvelteKit/Tauri structure**: Frontend at `frontend/` with SvelteKit (`src/routes`, `src/lib`). Tauri config at `src-tauri/`.
- **Existing routes**: `today`, `goals`, `mr-bloom`, `settings`, `auth`, `garden-selection`, `onboarding-preview`, `widget`, `widget-preview`.
- **Shared application shell**: `DesktopAppShell.svelte` composes `DesktopTitleBar` + `AppSidebar` + content slot. Uses `FixedCanvas` for 1280×800 constraint.
- **`DesktopAppShell` activeRoute type**: Currently `'TODAY' | 'GOALS' | 'MR. BLOOM' | 'SETTINGS'` — must add `'STATISTICS'`.
- **`AppSidebar`**: Hardcoded nav items using `SidebarNavigationItem`. Currently: TODAY, GOALS, MR. BLOOM, SETTINGS.
- **`SidebarNavigationItem`**: Accepts `icon: 'today' | 'goals' | 'chat' | 'settings'` — must add `'statistics'`.
- **`AppIcon`**: SVG-based icon component with `IconName` union type. Has `today`, `goals`, `chat`, `settings`, `document`, `calendar`, `clock`, `chevron-right`, `check_circle`, `check`, etc. Missing: `statistics` variant.
- **Shared styles**: CSS variables in `theme.css`. Key tokens: `--bloom-surface-cream`, `--bloom-border-subtle`, `--bloom-text-dark-blue`, `--bloom-text-muted-blue`, `--bloom-primary-green`, `--bloom-display-font`, `--bloom-body-font`, `--bloom-panel-title-size`, `--bloom-panel-title-weight`.
- **Feature module pattern**: `lib/features/{feature-name}/` with `components/{atoms,molecules,organisms}/`, `stores/`, `types.ts`.
- **Route pattern**: `+page.svelte` imports `DesktopAppShell` and renders feature organisms inside it.
- **Test pattern**: Vitest + @testing-library/svelte. Tests import page components, use `render`, `screen`, `fireEvent`.
- **Existing icons relevant to Statistics**: `clock` (for Study Time card), `calendar`/`today` (for Study Days card), `document` (for Plans card), `chevron-right` (for table row chevrons), `check_circle` and `check` (for completion status).

## Project Structure

### Documentation (this feature)

```text
specs/010-statistics-screen/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (NOT created by /speckit-plan)
```

### Source Code (repository root)

```text
frontend/src/
├── routes/
│   └── statistics/
│       └── +page.svelte                          # Statistics route page
└── lib/
    ├── features/
    │   └── statistics/
    │       ├── types.ts                           # All Statistics-specific types
    │       ├── data/
    │       │   └── mockData.ts                    # Typed mock fixtures
    │       ├── components/
    │       │   ├── atoms/
    │       │   │   ├── SummaryCard.svelte          # Single KPI card
    │       │   │   ├── CalendarDayCell.svelte       # Day cell in calendar grid
    │       │   │   ├── BarChartColumn.svelte        # Single bar in chart
    │       │   │   ├── FilterButton.svelte          # Filter pill button
    │       │   │   └── StatusBadge.svelte            # Completed/Unfinished badge
    │       │   ├── molecules/
    │       │   │   ├── DateRangeSelector.svelte      # Date range dropdown
    │       │   │   ├── CalendarMonthNav.svelte       # Month < label > controls
    │       │   │   ├── CalendarLegend.svelte          # Studied / No record legend
    │       │   │   ├── PlanHistoryRow.svelte           # Single table row
    │       │   │   └── PaginationControls.svelte       # Page nav controls
    │       │   └── organisms/
    │       │       ├── StatisticsHeader.svelte          # Title + subtitle + date selector
    │       │       ├── SummaryCardRow.svelte            # 3-card horizontal row
    │       │       ├── StudyCalendarPanel.svelte         # Full calendar panel
    │       │       ├── DailyStudyTimeChart.svelte        # Bar chart panel
    │       │       └── PlanHistoryPanel.svelte            # Table + filters + pagination
    │       └── StatisticsView.test.ts                    # Feature tests
    └── shared/
        └── components/
            ├── atoms/
            │   └── AppIcon.svelte                 # MODIFY: add 'statistics' to IconName, add SVG path
            ├── molecules/
            │   └── SidebarNavigationItem.svelte   # MODIFY: add 'statistics' to icon union type
            └── organisms/
                ├── AppSidebar.svelte              # MODIFY: add STATISTICS nav item between MR. BLOOM and SETTINGS
                └── DesktopAppShell.svelte          # MODIFY: add 'STATISTICS' to activeRoute union type
```

**Structure Decision**: Single feature module at `frontend/src/lib/features/statistics/` following the established `features/{name}/components/{atoms,molecules,organisms}` convention. No stores needed — local component state via `$state`/`$derived` is sufficient since data is read-only mock fixtures with simple local filter/pagination state.

## Architecture

### Shared Component Modifications

1. **`AppIcon.svelte`**: Add `'statistics'` to `IconName` union. Add SVG branch rendering three ascending vertical bars (simple bar-chart icon using `currentColor`).

2. **`SidebarNavigationItem.svelte`**: Add `'statistics'` to the `icon` prop union type.

3. **`AppSidebar.svelte`**: Add `<SidebarNavigationItem label="STATISTICS" icon="statistics" active={activeRoute === 'STATISTICS'} onClick={() => goto('/statistics')} />` between MR. BLOOM and SETTINGS.

4. **`DesktopAppShell.svelte`**: Add `'STATISTICS'` to the `activeRoute` union type.

### Feature-Specific Atoms

- **`SummaryCard.svelte`**: Renders one KPI card with an icon slot, label, and value. Props: `iconName: IconName`, `label: string`, `value: string`. Uses `--bloom-surface-cream` background, subtle border.
- **`CalendarDayCell.svelte`**: Renders a single day in the calendar grid. Props: `day: number`, `state: 'studied' | 'no-record' | 'inactive'`. Green fill for studied, neutral for no-record, muted for inactive/future.
- **`BarChartColumn.svelte`**: Renders a single vertical bar with value label above and weekday label below. Props: `day: string`, `hours: number`, `maxHours: number`. CSS height as percentage of max. Zero-value shows baseline marker.
- **`FilterButton.svelte`**: Pill-shaped filter button. Props: `label: string`, `active: boolean`, `onClick: () => void`. Active state shows light-blue background.
- **`StatusBadge.svelte`**: Completed (green check + pill) or Unfinished (gray circle + pill). Props: `status: 'Completed' | 'Unfinished'`. Uses icon shape + text label (not color alone per FR-036).

### Feature-Specific Molecules

- **`DateRangeSelector.svelte`**: Rounded button with calendar icon, date text, and dropdown chevron. Props: `ranges: StatisticsDateRange[]`, `selected: StatisticsDateRange`, `onSelect: (range) => void`. Simple dropdown implementation.
- **`CalendarMonthNav.svelte`**: Previous/next buttons flanking a centered month label. Props: `monthLabel: string`, `onPrev: () => void`, `onNext: () => void`. Buttons have `aria-label="Previous month"` / `"Next month"`.
- **`CalendarLegend.svelte`**: Two legend items: green square + "Studied", gray square + "No record".
- **`PlanHistoryRow.svelte`**: Single table row with date, plan name, tasks ratio, status badge, and chevron. Props: `entry: PlanHistoryEntry`, `onNavigate: (id) => void`.
- **`PaginationControls.svelte`**: Previous/next buttons with page indicator. Props: `currentPage: number`, `totalPages: number`, `onPageChange: (page) => void`. Buttons disabled at boundaries.

### Feature-Specific Organisms

- **`StatisticsHeader.svelte`**: Page heading (`h1`), subtitle, and date-range selector positioned right. Props: `ranges`, `selectedRange`, `onRangeChange`.
- **`SummaryCardRow.svelte`**: Horizontal flex row containing three `SummaryCard` instances. Props: `metrics: SummaryMetrics`.
- **`StudyCalendarPanel.svelte`**: Panel with `h2` title, `CalendarMonthNav`, weekday header row, 7-column day grid of `CalendarDayCell` components, and `CalendarLegend`. Internal state for current display month. Computes first-weekday offset and day count from typed data. Props: `studiedDays: CalendarDayState[]`.
- **`DailyStudyTimeChart.svelte`**: Panel with `h2` title, subtitle, and 7 `BarChartColumn` instances in a flex row. Props: `entries: DailyStudyEntry[]`, `subtitle: string`. Max height derived from max value.
- **`PlanHistoryPanel.svelte`**: Panel with `h2` title, filter buttons, table (`<table>` with `<th>` headers), paginated rows, and footer. Internal state for active filter and current page. Props: `entries: PlanHistoryEntry[]`, `itemsPerPage: number`.

### Page/Route Layer

- **`frontend/src/routes/statistics/+page.svelte`**: Imports `DesktopAppShell` with `activeRoute="STATISTICS"`. Renders `StatisticsHeader`, `SummaryCardRow`, a two-column grid for `StudyCalendarPanel` + `DailyStudyTimeChart`, and `PlanHistoryPanel`. All mock data imported from `data/mockData.ts`. Uses `$state` for selected date range.

## Interaction Plan

- **Sidebar navigation**: User clicks STATISTICS in sidebar → navigates to `/statistics`. Active state shown via `SidebarNavigationItem` active styling (light-blue pill).
- **Date range selection**: Clicking the date-range selector opens a dropdown. Selecting a range updates `selectedRange` state, which flows to summary cards, calendar, and chart as props. All ranges map to different typed mock data slices.
- **Calendar month navigation**: Previous/next buttons update internal month state. Grid recomputes day layout (weekday offset, day count). Panel size remains fixed.
- **Plan history filtering**: Clicking a filter button updates the active filter. Rows are filtered via `$derived`. Pagination resets to page 1 on filter change.
- **Pagination**: Previous/next buttons change current page. Rows sliced from filtered array. Buttons disabled at boundaries. Footer shows "Showing X of Y plans".
- **Row chevrons**: Interactive but navigate to no-op (plan details not yet implemented per spec assumptions).
- **Keyboard accessibility**: All interactive elements focusable via Tab. Activatable via Enter/Space. Visible focus rings via `--bloom-focus` or `outline: 2px solid #008ec5`.

## Visual Implementation Plan

### Layout Grid (within DesktopAppShell main area)

- **Overall**: Single column layout with vertical sections. Padding: `20px 24px`.
- **Row 1 (Header)**: Flex row. Title/subtitle left-aligned, date-range selector right-aligned.
- **Row 2 (Summary Cards)**: Flex row with 3 equal-width cards. Gap: `16px`.
- **Row 3 (Calendar + Chart)**: CSS Grid, two columns: `~45% / ~55%`. Gap: `16px`.
- **Row 4 (Plan History)**: Full-width panel.

### Card/Panel Styling

- Background: `#ffffff` (white cards on cream surface).
- Border: `1px solid` using `--bloom-border-subtle` (`#cac4b4`) or lighter `#DCE8EB`.
- Border-radius: `8px` (matching `--radius`).
- Internal padding: `16px 20px`.

### Typography

- Page title "STATISTICS": `--bloom-display-font` (pixel font), ~28px, deep navy `--bloom-text-dark-blue`.
- Subtitle: `--bloom-body-font`, ~14px, `--bloom-text-muted-blue`.
- Panel titles ("STUDY CALENDAR", etc.): `--bloom-body-font`, `--bloom-panel-title-size` (18px), `--bloom-panel-title-weight` (800), uppercase.
- KPI labels: uppercase, small, teal/blue accent.
- KPI values: large bold navy.
- Table text: `--bloom-body-font`, standard sizes.

### Colors

- Studied day: light green `#C8F0D0` background.
- No record: white/off-white.
- Inactive/future day: pale gray-blue `#EBF2F6`.
- Chart bars: `--bloom-primary-green` (`#66a46e`) or darker `#45A26B`.
- Completed badge: soft green `#DDF7E4` pill + green check.
- Unfinished badge: soft slate `#EBF1F5` pill + gray circle.
- Active filter: light blue `#CBE7FF` pill.

### Asset Strategy

1. **Existing reusable icons via `AppIcon`**: `clock` (Study Time), `calendar`/`today` (Study Days), `document` (Plans), `chevron-right` (row navigation), `check_circle` (Completed status).
2. **New icon variant**: `statistics` (three ascending vertical bars) — added as SVG path in `AppIcon.svelte`.
3. **No external image assets required**: All icons are inline SVG via `AppIcon` or simple CSS shapes (legend squares, status circles).

## Testing Strategy

- **Sidebar integration**: Verify STATISTICS appears between MR. BLOOM and SETTINGS. Verify navigation to `/statistics`. Verify active state.
- **Summary cards rendering**: Verify all three cards display correct labels and values.
- **Calendar rendering**: Verify June 2026 grid, correct studied/no-record states, month navigation.
- **Bar chart rendering**: Verify 7 bars with correct value labels, zero-day treatment.
- **Plan history filtering**: Verify filter buttons toggle, correct rows displayed per filter.
- **Pagination**: Verify page navigation, disabled states at boundaries, correct page indicator.
- **Empty states**: Verify empty filter results message.
- **Accessibility**: Verify `aria-label` on interactive elements, `aria-current="page"` on sidebar item, `<th>` in table, `h1`/`h2` headings.

## Visual Verification

1. Build and type-check: `npm run check` (from `frontend/`).
2. Run tests: `npm run test` (from `frontend/`).
3. Launch: `npm run tauri dev` (from project root).
4. Navigate to `/statistics`.
5. Compare side-by-side with `design-assets/app/references/statistic.png`.
6. Verify: layout proportions, typography, colors, icons, spacing, borders.
7. Verify: calendar day states, chart bar proportions, table alignment, status badges.
8. Fix any mismatches and repeat.
9. Confirm no console/terminal errors.
10. Confirm no imports from `design-assets/references`.

## Plan Deliverables

- **Exact existing file paths to modify**:
  - `frontend/src/lib/shared/components/atoms/AppIcon.svelte` (add `statistics` icon)
  - `frontend/src/lib/shared/components/molecules/SidebarNavigationItem.svelte` (add `statistics` to icon type)
  - `frontend/src/lib/shared/components/organisms/AppSidebar.svelte` (add STATISTICS nav item)
  - `frontend/src/lib/shared/components/organisms/DesktopAppShell.svelte` (add STATISTICS to activeRoute)
- **Exact proposed file paths**:
  - `frontend/src/routes/statistics/+page.svelte`
  - `frontend/src/lib/features/statistics/types.ts`
  - `frontend/src/lib/features/statistics/data/mockData.ts`
  - `frontend/src/lib/features/statistics/components/atoms/SummaryCard.svelte`
  - `frontend/src/lib/features/statistics/components/atoms/CalendarDayCell.svelte`
  - `frontend/src/lib/features/statistics/components/atoms/BarChartColumn.svelte`
  - `frontend/src/lib/features/statistics/components/atoms/FilterButton.svelte`
  - `frontend/src/lib/features/statistics/components/atoms/StatusBadge.svelte`
  - `frontend/src/lib/features/statistics/components/molecules/DateRangeSelector.svelte`
  - `frontend/src/lib/features/statistics/components/molecules/CalendarMonthNav.svelte`
  - `frontend/src/lib/features/statistics/components/molecules/CalendarLegend.svelte`
  - `frontend/src/lib/features/statistics/components/molecules/PlanHistoryRow.svelte`
  - `frontend/src/lib/features/statistics/components/molecules/PaginationControls.svelte`
  - `frontend/src/lib/features/statistics/components/organisms/StatisticsHeader.svelte`
  - `frontend/src/lib/features/statistics/components/organisms/SummaryCardRow.svelte`
  - `frontend/src/lib/features/statistics/components/organisms/StudyCalendarPanel.svelte`
  - `frontend/src/lib/features/statistics/components/organisms/DailyStudyTimeChart.svelte`
  - `frontend/src/lib/features/statistics/components/organisms/PlanHistoryPanel.svelte`
  - `frontend/src/lib/features/statistics/StatisticsView.test.ts`
- **Components to modify**:
  - `AppIcon.svelte` (add `'statistics'` to `IconName`, add SVG path)
  - `SidebarNavigationItem.svelte` (add `'statistics'` to icon union)
  - `AppSidebar.svelte` (add STATISTICS nav item)
  - `DesktopAppShell.svelte` (add `'STATISTICS'` to activeRoute union)
- **Components that must remain unchanged**:
  - Any component inside `features/today/`, `features/goals/`, `features/mr-bloom/`, `features/settings/`, `shared/styles/`
- **Implementation order**:
  1. Types and mock data
  2. Shared component modifications (AppIcon, SidebarNavigationItem, AppSidebar, DesktopAppShell)
  3. Feature atoms (SummaryCard, CalendarDayCell, BarChartColumn, FilterButton, StatusBadge)
  4. Feature molecules (DateRangeSelector, CalendarMonthNav, CalendarLegend, PlanHistoryRow, PaginationControls)
  5. Feature organisms (StatisticsHeader, SummaryCardRow, StudyCalendarPanel, DailyStudyTimeChart, PlanHistoryPanel)
  6. Route page (`/statistics/+page.svelte`)
  7. Tests
- **Testing order**:
  1. Sidebar integration tests
  2. Statistics page component tests
  3. Visual verification
- **Known risks and mitigation**:
  - Risk: Calendar grid first-weekday offset calculation. Mitigation: Use `new Date(year, month, 1).getDay()` with Monday-start adjustment.
  - Risk: Bar chart proportions not matching reference. Mitigation: Use relative percentage heights derived from max value; iterate on spacing.
  - Risk: Pixel font not matching reference exactly. Mitigation: Use `--bloom-display-font` which is the established pixel-style font.
- **Explicit out-of-scope items**:
  - Real backend statistics endpoints or data persistence
  - Plan detail page (row chevron destination)
  - Mobile, responsive, or alternate-resolution layouts
  - Animations (unless strictly needed for transitions)
  - Date-range picker complex UI (simple dropdown sufficient)
