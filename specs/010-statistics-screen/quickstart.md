# Quickstart: Statistics Screen

**Feature**: Statistics Screen | **Date**: 2026-09-15

## Prerequisites

- Node.js 18+ installed
- Rust toolchain installed (for Tauri)
- Project dependencies installed: `npm install` in `frontend/`

## Build & Validate

### 1. Type-check and lint

```bash
cd frontend
npm run check
```

**Expected outcome**: No TypeScript errors. Clean exit code 0.

### 2. Run tests

```bash
cd frontend
npm run test
```

**Expected outcome**: All tests pass, including new `StatisticsView.test.ts` tests.

### 3. Launch application

```bash
npm run tauri dev
```

**Expected outcome**: Application opens at 1280×800. Sidebar shows five navigation items.

## Validation Scenarios

### Scenario 1: Sidebar Integration

1. Open the application (any page).
2. **Verify**: Sidebar shows: TODAY, GOALS, MR. BLOOM, **STATISTICS**, SETTINGS (in that order).
3. **Verify**: STATISTICS item has a bar-chart icon.
4. Click STATISTICS.
5. **Verify**: Navigation goes to `/statistics`. STATISTICS item shows active light-blue background.
6. Click another sidebar item (e.g., TODAY).
7. **Verify**: Navigation proceeds normally. Active state moves to clicked item.
8. Tab-navigate to STATISTICS, press Enter.
9. **Verify**: Keyboard navigation works. Focus ring visible.

### Scenario 2: Page Header & Summary Cards

1. Navigate to `/statistics`.
2. **Verify**: Page heading reads "STATISTICS" in pixel font.
3. **Verify**: Subtitle reads "Your progress, one day at a time."
4. **Verify**: Date range selector shows "Jun 1 - 14, 2026" with calendar icon and chevron.
5. **Verify**: Three summary cards in a horizontal row:
   - Study Time: clock icon, "STUDY TIME", "24h 30m"
   - Study Days: calendar icon, "STUDY DAYS", "10 days"
   - Plans: document icon, "PLANS", "8 complete / 3 unfinished"

### Scenario 3: Study Calendar

1. On the Statistics page, locate the Study Calendar panel.
2. **Verify**: Panel title "STUDY CALENDAR".
3. **Verify**: Month label "June 2026" with < > navigation buttons.
4. **Verify**: Weekday headers: Mon, Tue, Wed, Thu, Fri, Sat, Sun.
5. **Verify**: Days 1–9, 11, 12, 14 are green ("studied").
6. **Verify**: Other days in June are neutral ("no record").
7. **Verify**: Legend shows green square + "Studied", gray square + "No record".
8. Click the next-month button (>).
9. **Verify**: Calendar shows July 2026. Grid updates. Panel size unchanged.
10. Click the previous-month button (<).
11. **Verify**: Calendar returns to June 2026.

### Scenario 4: Daily Study Time Chart

1. Locate the Daily Study Time panel.
2. **Verify**: Panel title "DAILY STUDY TIME", subtitle "Jun 8 - 14".
3. **Verify**: Seven vertical bars with labels:
   - Mon: 2h, Tue: 3h, Wed: 0h, Thu: 2.5h, Fri: 4h, Sat: 0h, Sun: 3h
4. **Verify**: Value labels appear above each bar.
5. **Verify**: Wed and Sat (0h) show a small baseline marker.
6. **Verify**: Fri (4h) is the tallest bar.

### Scenario 5: Plan History Table

1. Locate the Plan History panel.
2. **Verify**: Panel title "PLAN HISTORY".
3. **Verify**: Filter buttons: All (active), Completed, Unfinished.
4. **Verify**: Table columns: DATE, PLAN, TASKS, STATUS.
5. **Verify**: Four rows displayed:
   - Jun 14 | Learn machine learning | 3 / 3 | ✔ Completed
   - Jun 12 | Build backend API | 2 / 3 | ○ Unfinished
   - Jun 11 | Study databases | 3 / 3 | ✔ Completed
   - Jun 9 | Refine Blooming UI | 1 / 3 | ○ Unfinished
6. **Verify**: Each row has a right chevron (>).
7. **Verify**: Footer shows "Showing 4 of 11 plans".
8. **Verify**: Pagination shows < 1 / 3 > with < disabled.

### Scenario 6: Filtering

1. Click the "Completed" filter button.
2. **Verify**: "Completed" button shows active (light-blue) state. "All" returns to default.
3. **Verify**: Only Completed rows are visible.
4. Click the "Unfinished" filter button.
5. **Verify**: Only Unfinished rows are visible.
6. Click "All".
7. **Verify**: All rows visible again.

### Scenario 7: Pagination

1. With "All" filter active, click the next-page button (>).
2. **Verify**: Table shows page 2 data. Page indicator reads "2 / 3".
3. **Verify**: Previous button is now enabled.
4. Click next again.
5. **Verify**: Page indicator reads "3 / 3". Next button is disabled.
6. Click previous.
7. **Verify**: Returns to page 2.

### Scenario 8: Visual Comparison

1. Open `design-assets/app/references/statistic.png` side-by-side with the running app.
2. **Verify**: Layout proportions match (sidebar width, panel sizes, card sizes).
3. **Verify**: Typography matches (pixel font for title, sans-serif for body).
4. **Verify**: Colors match (green for studied days and bars, blue for active states).
5. **Verify**: Spacing and borders match.
6. **Verify**: No content overflows the 1280×800 canvas.

### Scenario 9: No Regressions

1. Navigate to each existing page: Today, Goals, Mr. Bloom, Settings.
2. **Verify**: Each page loads and renders correctly.
3. **Verify**: Sidebar shows STATISTICS on all pages.
4. **Verify**: No console errors or warnings.

## Type and Data Model References

- Full type definitions: [data-model.md](./data-model.md)
- Mock data fixtures: `frontend/src/lib/features/statistics/data/mockData.ts` (created during implementation)
