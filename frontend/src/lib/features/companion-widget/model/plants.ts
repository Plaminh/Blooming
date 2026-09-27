import type {
  PlantFrameIndex,
  PlantSpecies,
} from "../types/presentation";
import type { AtlasCell } from "./atlas";

export const PLANT_ATLAS = {
  sheetWidth: 1024,
  sheetHeight: 1024,
  columns: 4,
  rows: 4,
  cellWidth: 256,
  cellHeight: 256,
  displayHeight: 148,
} as const;

export const WATERING_ATLAS = {
  src: "/assets/plants/watering-spritesheet.png",
  sheetWidth: 1024,
  sheetHeight: 512,
  columns: 4,
  rows: 2,
  frameCount: 8,
  displayHeight: 165,
  frameDurationMs: 110,
} as const;

export const PLANT_SPECIES = [
  "monstera",
  "sunflower",
  "bonsai",
  "jasmine",
  "lavender",
] as const satisfies readonly PlantSpecies[];

export const PLANT_SOURCES: Record<PlantSpecies, string> = {
  monstera: "/assets/plants/monstera-spritesheet.png",
  sunflower: "/assets/plants/sunflower-spritesheet.png",
  bonsai: "/assets/plants/bonsai-spritesheet.png",
  jasmine: "/assets/plants/jasmine-spritesheet.png",
  lavender: "/assets/plants/lavender-spritesheet.png",
};

export function clampPlantFrameIndex(frame: number): PlantFrameIndex {
  if (!Number.isFinite(frame)) return 0;
  return Math.min(
    PLANT_ATLAS.columns * PLANT_ATLAS.rows - 1,
    Math.max(0, Math.trunc(frame)),
  ) as PlantFrameIndex;
}

export function plantCellForFrame(frame: number): AtlasCell {
  const safeFrame = clampPlantFrameIndex(frame);
  return {
    col: safeFrame % PLANT_ATLAS.columns,
    row: Math.floor(safeFrame / PLANT_ATLAS.columns),
  };
}

export function plantSource(species: PlantSpecies): string {
  return PLANT_SOURCES[species];
}

export function plantSheetTransform(
  frame: number,
  scale: number,
): string {
  const cell = plantCellForFrame(frame);
  return `scale(${scale}) translate(${
    -cell.col * PLANT_ATLAS.cellWidth
  }px, ${-cell.row * PLANT_ATLAS.cellHeight}px)`;
}
