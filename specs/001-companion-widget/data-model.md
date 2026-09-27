# Data Model: Compact Desktop Companion Widget

This feature has no database tables, ORM models, or HTTP resources. The model is the TypeScript presentation contract consumed by `CompanionWidget.svelte`. Mock values live in `fixtures/` and must not be hard-coded inside production component branches beyond accepting typed props.

Canonical file at implementation: `frontend/src/lib/features/companion-widget/types/presentation.ts`.

## Discriminated union

Exactly one active `kind`. No other presentation kinds.

```typescript
export type CompanionWidgetKind =
  | "paused"
  | "behindSchedule"
  | "offline"
  | "reminders";

export type CompanionWidgetPresentation =
  | PausedPresentation
  | BehindSchedulePresentation
  | OfflinePresentation
  | RemindersPresentation;

export type ReminderItem = {
  id: string;
  /** Full accessible and visual source text. CSS may ellipsis; do not truncate this string. */
  label: string;
};
```

Svelte 5 component props use `$props()` and a typed props object.

### `PausedPresentation`

| Field | Type | Required | Notes |
|---|---|---|---|
| `kind` | `"paused"` | yes | Discriminator |
| `speechText` | `string` | yes | Fixture: `Paused. Take your time.` |
| `timeText` | `string` | no | Fixture: `"18:42"`. If omitted, render no timer; do not invent a clock |
| `onResume` | `() => void` | no | Missing must not throw |
| `onEnd` | `() => void` | no | Missing must not throw |

Character: atlas row `7`, columns `[0, 1, 2, 3]` in order. Paused uses the cyan sleep effects baked into those frames. There is no separate sleep overlay. The shared `activePlant` field is fixture-only. Buttons: **RESUME** (primary, play) then **END** (secondary, stop). Both stay rendered when a callback is absent; invoke the matching optional callback only when present.

### `BehindSchedulePresentation`

| Field | Type | Required | Notes |
|---|---|---|---|
| `kind` | `"behindSchedule"` | yes | |
| `speechText` | `string` | yes | Fixture: `We are 35 minutes behind. Adjust the remaining plan?` |
| `onReplan` | `() => void` | no | |
| `onLater` | `() => void` | no | |
| `onOpen` | `() => void` | no | |

No `timeText` field on this variant (cannot display a timer). Character: atlas row `6`, columns `[0, 2]`, plus orange alerts. Buttons left to right: **REPLAN** (primary), **LATER**, **OPEN**.

### `OfflinePresentation`

| Field | Type | Required | Notes |
|---|---|---|---|
| `kind` | `"offline"` | yes | |
| `speechText` | `string` | yes | Fixture: `Offline – changes will sync later.` |
| `timeText` | `string` | no | Fixture: `"14:06"` |

No callback fields. No action buttons. Character: atlas row `3`, columns `[0, 1, 2, 3]`, plus Wi-Fi and red `×`.

### `RemindersPresentation`

| Field | Type | Required | Notes |
|---|---|---|---|
| `kind` | `"reminders"` | yes | |
| `reminders` | `ReminderItem[]` | yes | Fixture has two items |
| `onView` | `() => void` | no | |
| `onDismiss` | `() => void` | no | |

Heading: `1 REMINDER` vs `{n} REMINDERS`. Show at most two labels; if `length > 2`, add compact `+N more` (`N = length - 2`) without growing widget height. Zero reminders is not a selected presentation for this feature. Character: atlas row `4`, column `[1]`, plus pink alerts. Panel bell is SVG, not an atlas cell. Buttons: **VIEW** (primary) then **DISMISS**. Each list item’s accessible name is the full `label` even when the visual line is ellipsized.

## Organism props

```typescript
export type CompanionWidgetProps = {
  presentation: CompanionWidgetPresentation;
};
```

`CompanionWidget` must not import fixture modules in a way that embeds mock strings as the only possible copy. The production `/widget` page may pass `pausedFixture` as the default **page-level** presentation until a future feature owns state selection. The development selector lives only on `/widget-preview` and must not be rendered inside `CompanionWidget`.

## Atlas record (not domain state)

```typescript
export const MR_BLOOM_ATLAS = {
  src: "/assets/mr-bloom/mr-bloom-spritesheet.png",
  sheetWidth: 1152,
  sheetHeight: 1152,
  columns: 4,
  rows: 8,
  cellWidth: 288,
  cellHeight: 144,
  frameIntervalMs: 550,
} as const;

export const MR_BLOOM_ROWS = {
  paused: 7,
  behindSchedule: 6,
  offline: 3,
  reminders: 4,
} as const;

export const MR_BLOOM_FRAME_SEQUENCE = {
  paused: [0, 1, 2, 3],
  behindSchedule: [0, 2],
  offline: [0, 1, 2, 3],
  reminders: [1],
} as const;
```

Authoritative mapping, zero-based `[col, row]` from the top-left of the normalized sheet. Animation walks only the configured sequence for the selected state.

| `kind` | Row | Pose in the supplied sheet |
|---|---|---|
| `offline` | `3` | Waiting / thinking |
| `reminders` | `4` | Alert / waving |
| `behindSchedule` | `6` | Worried / sad |
| `paused` | `7` | Sleeping |

The source artwork is an irregular **1536 × 1152** sheet: rows are exactly 144px high, but its four sprites are not 384px cells and the first seven pixel rows can contain bleed from the preceding row. The normalized runtime sheet is **1152 × 1152**, **4 × 8**, with **288 × 144** cells; normalization clears that centered boundary bleed while preserving detached right-edge effects. Invariants: every permitted frame stays inside the selected row; offsets are whole pixels (`col * 288`, `row * 144`); the viewport shows exactly one cell; animation resets to the sequence's first column on kind changes; reduced motion freezes there. Non-paused states continue to exclude baked effects that conflict with their separate semantic overlays.

Every presentation also carries fixture-only plant data until application state owns it:

```typescript
activePlant: { species: PlantSpecies; frameIndex: PlantFrameIndex };
```

`PlantSpecies` is `monstera | sunflower | bonsai | jasmine | lavender`. `PlantFrameIndex` is `0` through `15`. Plant frames are lifecycle stages, not an animation loop. Real reward and garden logic stay outside this feature.

## Layout record (not domain state)

`model/layout.ts` is the single typed source of state geometry on the fixed canvas. `WIDGET_LAYOUTS[kind]` supplies the panel rect, character and status anchors, plant anchor, optional timer position, and action-row metrics, emitted as CSS custom properties on the widget root.

Implemented shared origins:

```typescript
export const PANEL_POSITION = { x: 215, y: 60 } as const;
export const MR_BLOOM_POSITION = { left: 70, bottom: 4 } as const;
```

| `kind` | Panel size | Timer | Action `top` / `right` / `gap` | Primary × secondary × height |
|---|---|---|---|---|
| `paused` | `250 × 86` | `78 / 18` | `220 / 12 / 9` | `164 × 132 × 58` |
| `behindSchedule` | `366 × 90` | none | `213 / 14 / 7` | `129 × 149 × 58` |
| `offline` | `252 × 111` | `78 / 20` | `220 / 12 / 9` | `164 × 132 × 58` |
| `reminders` | `328 × 128` | none | `210 / 14 / 9` | `129 × 149 × 58` |

Invariants:

- Every `kind` has an entry; only `paused` and `offline` define `timer`.
- All four states share `PANEL_POSITION` (`x: 215`, `y: 60`) and the character anchor. Panel width and height differ per state.
- `character.left` / `character.bottom` place the normalized cell's `220 × 110` rendered viewport; the shared value is `(70, 4)`.
- The active plant uses `(left: -4, bottom: 4)` in all four states and is layered behind Mr. Bloom.
- Character, status, and plant coordinates live here, not in component CSS.
- Shared visual tokens (colors, stroke, radius, font) stay in `styles/widget-theme.css`; coordinates do not.

## Background record

```typescript
export const WIDGET_SCENE = {
  skySrc: "/assets/widget/environment/daytime/morning.png",
  bushesSrc: "/assets/widget/environment/season/spring.png",
  frameWidth: 1880,  // sky width; clip bushes to this
  frameHeight: 837,  // sky height
  bushesWidth: 1881,
  bushesHeight: 836,
  anchor: "bottom-left",
} as const;
```

## State transitions

This feature does **not** implement a domain state machine. Preview buttons replace `presentation` on the preview page only. Production `/widget` does not switch kinds. Future session/reminder/connectivity engines must map into this union rather than adding a fifth `kind` here.

## Validation rules

- `kind` is one of the four literals; TypeScript exhaustiveness in `{#if presentation.kind === ...}` / `switch`.
- Do not pass behind-schedule or reminders callbacks into paused/offline objects.
- Do not read `timeText` except on `paused` and `offline`.
- `ReminderItem.label` is non-empty for fixture data.
- Window control handlers are Tauri adapter concerns in `WidgetTitleBar`, not fields on `CompanionWidgetPresentation`.
- No presentation field or asset URL may point at source-only art (see [spec.md](./spec.md) VR-015).

## Four fixtures (values, not component logic)

| Export | `kind` | Notable values |
|---|---|---|
| `pausedFixture` | `paused` | speech `Paused. Take your time.`; `timeText` `"18:42"`; mock `onResume` / `onEnd` |
| `behindScheduleFixture` | `behindSchedule` | speech `We are 35 minutes behind. Adjust the remaining plan?`; no time; mock `onReplan` / `onLater` / `onOpen` |
| `remindersFixture` | `reminders` | items `Start Database`, `Review milestone`; mock `onView` / `onDismiss` |
| `offlineFixture` | `offline` | speech `Offline – changes will sync later.`; `timeText` `"14:06"`; no callbacks |

Preview may also pass copies with omitted `timeText` / omitted callbacks for edge-case checks.
