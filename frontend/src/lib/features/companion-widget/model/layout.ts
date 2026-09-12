import type { CompanionWidgetKind } from "../types/presentation";

type Point = {
  x: number;
  y: number;
};

type Rect = Point & {
  width: number;
  height: number;
};

/**
 * `left` and `bottom` place the 220 × 110 rendered character cell.
 */
type CharacterLayout = {
  left: number;
  bottom: number;
  status: Point;
};

type PlantLayout = {
  left: number;
  bottom: number;
};

type ActionLayout = {
  top: number;
  right: number;
  gap: number;
  primaryWidth: number;
  secondaryWidth: number;
  height: number;
  compactPrimaryWidth: number;
  compactSecondaryWidth: number;
};

export type WidgetVisualLayout = {
  panel: Rect;
  character: CharacterLayout;
  plant: PlantLayout;
  timer?: {
    top: number;
    right: number;
  };
  actions: ActionLayout;
};

export const MR_BLOOM_POSITION = {
  left: 70,
  bottom: 4,
} as const;

export const PANEL_POSITION = {
  x: 215,
  y: 60,
} as const;

export const WIDGET_LAYOUTS: Record<CompanionWidgetKind, WidgetVisualLayout> = {
  paused: {
    panel: { ...PANEL_POSITION, width: 250, height: 86 },
    character: { ...MR_BLOOM_POSITION, status: { x: 90, y: 36 } },
    plant: { left: -4, bottom: 4 },
    timer: { top: 78, right: 18 },
    actions: {
      top: 220,
      right: 12,
      gap: 9,
      primaryWidth: 164,
      secondaryWidth: 132,
      height: 58,
      compactPrimaryWidth: 124,
      compactSecondaryWidth: 114,
    },
  },
  behindSchedule: {
    panel: { ...PANEL_POSITION, width: 366, height: 90 },
    character: { ...MR_BLOOM_POSITION, status: { x: 168, y: 76 } },
    plant: { left: -4, bottom: 4 },
    actions: {
      top: 213,
      right: 14,
      gap: 7,
      primaryWidth: 129,
      secondaryWidth: 149,
      height: 58,
      compactPrimaryWidth: 124,
      compactSecondaryWidth: 114,
    },
  },
  offline: {
    panel: { ...PANEL_POSITION, width: 252, height: 111 },
    character: { ...MR_BLOOM_POSITION, status: { x: 163, y: 70 } },
    plant: { left: -4, bottom: 4 },
    timer: { top: 78, right: 20 },
    actions: {
      top: 220,
      right: 12,
      gap: 9,
      primaryWidth: 164,
      secondaryWidth: 132,
      height: 58,
      compactPrimaryWidth: 124,
      compactSecondaryWidth: 114,
    },
  },
  reminders: {
    panel: { ...PANEL_POSITION, width: 328, height: 128 },
    character: { ...MR_BLOOM_POSITION, status: { x: 172, y: 79 } },
    plant: { left: -4, bottom: 4 },
    actions: {
      top: 210,
      right: 14,
      gap: 9,
      primaryWidth: 129,
      secondaryWidth: 149,
      height: 58,
      compactPrimaryWidth: 124,
      compactSecondaryWidth: 114,
    },
  },
};

export function widgetLayoutStyle(kind: CompanionWidgetKind): string {
  const layout = WIDGET_LAYOUTS[kind];
  const variables = [
    `--widget-panel-left:${layout.panel.x}px`,
    `--widget-panel-top:${layout.panel.y}px`,
    `--widget-panel-width:${layout.panel.width}px`,
    `--widget-panel-height:${layout.panel.height}px`,
    `--widget-character-left:${layout.character.left}px`,
    `--widget-character-bottom:${layout.character.bottom}px`,
    `--widget-status-left:${layout.character.status.x}px`,
    `--widget-status-top:${layout.character.status.y}px`,
    `--widget-plant-left:${layout.plant.left}px`,
    `--widget-plant-bottom:${layout.plant.bottom}px`,
    `--widget-action-top:${layout.actions.top}px`,
    `--widget-action-right:${layout.actions.right}px`,
    `--widget-action-gap:${layout.actions.gap}px`,
    `--widget-btn-primary-w:${layout.actions.primaryWidth}px`,
    `--widget-btn-secondary-w:${layout.actions.secondaryWidth}px`,
    `--widget-btn-height:${layout.actions.height}px`,
    `--widget-compact-primary-w:${layout.actions.compactPrimaryWidth}px`,
    `--widget-compact-secondary-w:${layout.actions.compactSecondaryWidth}px`,
  ];

  if (layout.timer) {
    variables.push(
      `--widget-timer-top:${layout.timer.top}px`,
      `--widget-timer-right:${layout.timer.right}px`,
    );
  }

  return variables.join(";");
}
