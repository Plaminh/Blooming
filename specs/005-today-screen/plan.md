# Implementation Plan: Today Screen

## 1. Technical Context & Constitution Check
- **Framework**: SvelteKit, TypeScript, Tauri 2.
- **Styling Pipeline**: Global tokens/utility classes (based on existing features). The appended React code uses Tailwind, but we will adapt to the project's actual CSS strategy (likely raw CSS with tokens or scoped CSS given the lack of Tailwind components discovered).
- **Constitution Check**: We must use typed local state for development fixtures. We must avoid React/JSX. The Today screen layout must strictly match the screenshot.

## 2. Asset Inventory
The following assets are required based on the visual reference. Many are missing and are reported below as per constraints:

**Available Assets:**
- Large Plant: `static/assets/plants/monstera-spritesheet.png` (Requires sprite crop).
- Leaf Icon: `static/assets/icons/leaf-icon.png` (Used for leaf counter and task category).
- Mr. Bloom: `static/assets/mr-bloom/mr-bloom-spritesheet.png` (Used for Replan button or sidebar, requires sprite crop).
- Window Controls / Shared App Icons: Rendered via existing components or Tauri APIs.

**Missing Assets (Reported):**
- Timeline Task Category Icons: Book icon (Study), Clipboard icon (Proposal), Shoe icon (Walk).
- Sidebar Icons: Calendar (Today), Chat bubble (Mr. Bloom), Gear (Settings).
- Date Navigation Icons: Left arrow, Right arrow.
- Checkmark (Completed task status).
- Water drop (Water counter).
- Edit pencil (Edit Manually action).
- Refresh arrows (Replan action).
- Question mark (Focus Setup).
- Play arrow (Start Focus).
- Next Session calendar icon.
- Background/Frame textures or repeating patterns (if any).

*Note: Missing icons will be implemented as labeled placeholders or text fallbacks if the design files are truly absent in the repository.*

## 3. Atomic Design Map

**Atoms**
- `src/lib/features/today/components/atoms/StatusBadge.svelte`
- `src/lib/features/today/components/atoms/TimelineMarker.svelte`
- `src/lib/features/today/components/atoms/FocusPresetButton.svelte`
- `src/lib/features/today/components/atoms/SidebarIcon.svelte`
- `src/lib/features/today/components/atoms/ActionButton.svelte`

**Molecules**
- `src/lib/features/today/components/molecules/SidebarItem.svelte`
- `src/lib/features/today/components/molecules/TimelineCard.svelte`
- `src/lib/features/today/components/molecules/DateNavigator.svelte`
- `src/lib/features/today/components/molecules/TaskDetailRow.svelte`
- `src/lib/features/today/components/molecules/FocusSetupOptions.svelte`

**Organisms**
- `src/lib/features/today/components/organisms/TodaySidebar.svelte`
- `src/lib/features/today/components/organisms/TodayTimeline.svelte`
- `src/lib/features/today/components/organisms/RightRail.svelte`
  - Includes panels for Task Details, Next Session, Focus Setup, and Your Garden.
- `src/lib/features/today/components/organisms/BottomActions.svelte`

**Pages**
- `src/routes/today/+page.svelte` (or equivalent root route mapped for this feature)

## 4. Typed View Model
```typescript
type TaskStatus = 'in-progress' | 'completed' | 'upcoming';
type TaskCategory = 'Learning' | 'Work' | 'Personal'; // Derived from fixtures

interface Task {
  id: string;
  title: string;
  startTime: string; // e.g. "09:00"
  endTime: string;
  durationString: string; // e.g. "(1 hour)"
  status: TaskStatus;
  category: TaskCategory;
  notes?: string;
  iconRef?: string;
}

type FocusPreset = '25/5' | '50/10' | 'Custom';
```
*(No CSS utility classes will be stored in this domain data.)*

## 5. Layout Strategy (1440x900)
- **Container**: 1440x900 fixed size for desktop app frame.
- **Title Bar**: Custom turquoise bar at the top, integrating Tauri drag regions and window controls.
- **Three Columns**:
  1. **Sidebar**: Fixed width (approx 173px), holding navigation and plant asset.
  2. **Timeline**: Fluid/flex taking remaining space (approx 620px). Scrollable or constrained.
  3. **Right Rail**: Fixed width (approx 440px), stacked panels with fixed margins.
- **Bottom Actions**: Fixed height block pinned to the bottom of the timeline area.

## 6. State and Event Flow
- **Date Navigation**: Local state variable `currentDate` changes on prev/next button clicks.
- **Task Selection**: Local state variable `selectedTaskId`. Timeline card click updates this variable, triggering reactivity in Task Details panel.
- **Focus Preset**: Local state `selectedFocusPreset`. Only one can be active.
- **Start Focus**: Triggers custom event or logs if no backend.
- **Tauri Controls**: Calls `@tauri-apps/api/window` methods (minimize, toggleMaximize, close).

## 7. Accessibility
- All interactive elements (timeline cards, focus presets, actions, sidebar items) will use native `<button>` tags or `tabindex="0"` with keyboard handlers.
- `aria-selected` will be used for selected tasks, presets, and active sidebar items.

## 8. Verification Strategy
1. Load font and CSS framework on an empty page.
2. Construct the layout scaffolding (Sidebar, Timeline, Right Rail).
3. Place fixed-size containers based on screenshot analysis.
4. Render components with mock View Model data.
5. Capture a full-screen screenshot at 1440x900.
6. Compare with `removed reference artwork`.
7. Iterate on margins, padding, and colors to minimize deviation.

## 9. Risks and Mitigations
- **Missing Assets**: Many assets are missing. We will use text-based fallbacks or solid color rectangles sized appropriately, and clearly report them as missing.
- **CSS Pipeline Failure**: If Tailwind is not installed properly, we will use plain CSS classes to ensure styling is applied.
- **Title Bar Regressions**: We will reuse any shared title bar if it exists, otherwise we'll build a scoped one that fits the Today layout without breaking other layouts.
