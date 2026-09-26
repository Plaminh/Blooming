# UI Contract: Today Execution Dashboard Components

**Feature**: `028-today-execution-dashboard`  
**Date**: 2026-09-26  

---

## 1. `RightRail.svelte` Component Contract

### Component Props
```typescript
interface RightRailProps {
  task: Task | undefined;
  nextTask: Task | undefined;
  selectedFocusPreset: FocusPreset;
  customFocusMinutes: number;
  customBreakMinutes: number;
  focusDisabled?: boolean;
  onPresetSelect: (preset: FocusPreset) => void;
  onCustomSaved: (focusMinutes: number, breakMinutes: number) => void;
  onStartFocus: () => void;
  onMarkComplete: (taskId: string) => Promise<void>;
  onAdjustWithMrBloom: (taskId: string) => void;
}
```

### Visual & Interactive Specification
1. **Header**:
   - Title: `"TASK DETAILS"`.
   - Actions: **None** (Pencil icon, edit toggle, Save/Cancel buttons removed).
2. **Metadata Body (Read-Only)**:
   - Summary: Task icon, Title (`<h3>`), scheduled start-end time and duration string.
   - Description / Notes: Static text (or `"No description."`).
   - Category: Static badge (`"Learning" | "Work" | "Personal" | "Uncategorized"`). No dropdown.
   - Status: Read-only badge (`"Upcoming" | "In-Progress" | "Completed"`).
3. **Actions Panel**:
   - `START FOCUS`: Triggers `onStartFocus()`. Disabled when `focusDisabled`, no task selected, or task is completed.
   - `MARK COMPLETE`: Triggers `onMarkComplete(task.task_id)`. Disabled if no `task.task_id` or task already `completed`.
   - `ADJUST WITH MR. BLOOM`: Triggers `onAdjustWithMrBloom(task.task_id)`. Secondary action button with Mr. Bloom leaf/sparkle icon.

---

## 2. `BottomActions.svelte` Component Contract

### Component Props
```typescript
interface BottomActionsProps {
  disabled?: boolean;
  onQuickReplan: () => void;
  onAdjustWithMrBloom: () => void;
}
```

### Visual & Interactive Specification
1. **Primary Action**:
   - Button label: `"ADJUST WITH MR. BLOOM"`
   - Icon: `AppIcon name="replan"`
   - Handler: `onAdjustWithMrBloom`
   - Purpose: Navigates to `/mr-bloom?date=...` for structural modifications.
2. **Secondary Action**:
   - Button label: `"QUICK REPLAN"`
   - Icon: `AppIcon name="calendar"` or clock
   - Handler: `onQuickReplan`
   - Purpose: Invokes deterministic scheduler to realign remaining blocks from current time.
3. **Removed**:
   - `"EDIT MANUALLY"` button is removed entirely.
