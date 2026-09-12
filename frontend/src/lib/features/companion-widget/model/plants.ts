import type {
  PlantFrameIndex,
  PlantSpecies,
} from "../types/presentation";
import type { AtlasCell } from "./atlas";

export const PLANT_ATLAS = {
  sheetWidth: 2304,
  sheetHeight: 896,
  columns: 8,
  rows: 2,
  cellWidth: 288,
  cellHeight: 448,
  displayHeight: 148,
} as const;

export const PLANT_SPECIES = [
  "monstera",
  "sunflower",
  "bonsai",
  "jasmine",
  "lavender",
] as const satisfies readonly PlantSpecies[];

export const PLANT_SOURCES: Record<PlantSpecies, string> = {
  monstera: "/assets/widget/plants/monstera-spritesheet.png",
  sunflower: "/assets/widget/plants/sunflower-spritesheet.png",
  bonsai: "/assets/widget/plants/bonsai-spritesheet.png",
  jasmine: "/assets/widget/plants/jasmine-spritesheet.png",
  lavender: "/assets/widget/plants/lavender-spritesheet.png",
};

export function clampPlantFrameIndex(frame: number): PlantFrameIndex {
  if (!Number.isFinite(frame)) return 0;
  return Math.min(15, Math.max(0, Math.trunc(frame))) as PlantFrameIndex;
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
