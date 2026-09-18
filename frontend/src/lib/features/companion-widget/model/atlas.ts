import type { CompanionWidgetKind } from "../types/presentation";

export const MR_BLOOM_ATLAS = {
  src: "/assets/widget/characters/mr-bloom-spritesheet.png",
  sheetWidth: 1152,
  sheetHeight: 1152,
  columns: 4,
  rows: 8,
  cellWidth: 288,
  cellHeight: 144,
  frameIntervalMs: 550,
} as const;

export type AtlasCell = {
  col: number;
  row: number;
};

export const MR_BLOOM_CHAT_ANIMATIONS = {
  idle: {
    row: 0,
    frames: [{ col: 2, durationMs: 3000 }, { col: 1, durationMs: 140 }],
  },
  thinking: {
    row: 2,
    frames: [0, 1, 2, 3].map((col) => ({ col, durationMs: 250 })),
  },
} as const;

export type MrBloomChatAnimation = keyof typeof MR_BLOOM_CHAT_ANIMATIONS;

/**
 * Confirmed by inspecting the 4 × 8 sheet, top-left origin, zero-based rows:
 * row 3 waiting/thinking, row 4 alert/waving, row 6 worried/sad, row 7 sleeping.
 */
export const MR_BLOOM_ROWS: Record<CompanionWidgetKind, number> = {
  focusing: 3,
  ending: 4,
  paused: 7,
  behindSchedule: 6,
  offline: 3,
  reminders: 4,
};

/** Columns whose baked effects do not conflict with each state's overlay. */
export const MR_BLOOM_FRAME_SEQUENCE = {
  focusing: [0, 1, 2, 3],
  ending: [0, 1],
  paused: [0, 1, 2, 3],
  behindSchedule: [0, 2],
  offline: [0, 1, 2, 3],
  reminders: [1],
} as const satisfies Record<CompanionWidgetKind, readonly number[]>;

export const WIDGET_SCENE = {
  frameWidth: 1880,
  frameHeight: 837,
  bushesWidth: 1881,
  bushesHeight: 836,
  bushesOffsetY: -65,
  anchor: "bottom-left",
} as const;

export function atlasCellOffset(cell: AtlasCell): { x: number; y: number } {
  return {
    x: cell.col * MR_BLOOM_ATLAS.cellWidth,
    y: cell.row * MR_BLOOM_ATLAS.cellHeight,
  };
}

export function atlasSheetTransform(cell: AtlasCell, scale: number): string {
  const { x, y } = atlasCellOffset(cell);
  // CSS applies transform functions right-to-left. Translate in unscaled
  // sheet space first, then scale, so only the target cell is shown.
  return `scale(${scale}) translate(${-x}px, ${-y}px)`;
}

export function atlasFrameColumn(
  kind: CompanionWidgetKind,
  sequenceIndex: number,
): number {
  const sequence = MR_BLOOM_FRAME_SEQUENCE[kind];
  if (!Number.isFinite(sequenceIndex)) return sequence[0];
  return sequence[Math.max(0, Math.trunc(sequenceIndex)) % sequence.length];
}

export function atlasCellForKind(kind: CompanionWidgetKind, sequenceIndex = 0): AtlasCell {
  return {
    col: atlasFrameColumn(kind, sequenceIndex),
    row: MR_BLOOM_ROWS[kind],
  };
}
