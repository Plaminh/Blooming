import { describe, expect, it } from "vitest";
import type { GardenState, GrowthStage } from "$lib/api/types";
import {
  PLANT_SPRITE_CONFIG,
  getPlantFrame,
  selectedPlantPresentation,
} from "./spriteMapper";
import type { PlantSpecies } from '$lib/shared/sprites/types';

const species: PlantSpecies[] = ["sunflower", "bonsai", "jasmine", "lavender", "monstera"];

describe("plant sprite mapping", () => {
  it.each(species)("maps %s to its new spritesheet", (plant) => {
    expect(PLANT_SPRITE_CONFIG[plant].src).toBe(`/assets/plants/${plant}-spritesheet.png`);
  });

  it("maps growth rows and vitality columns deterministically", () => {
    const stages: GrowthStage[] = ["SPROUTING", "GROWING", "BLOOMING", "FLOURISHING"];
    const vitality = [100, 60, 30, 0];
    for (const [row, stage] of stages.entries()) {
      for (const [column, value] of vitality.entries()) {
        expect(getPlantFrame("sunflower", stage, value)).toBe(row * 4 + column);
      }
    }
  });

  it("changes species without changing the semantic frame", () => {
    const garden: GardenState = {
      water_balance: 1,
      leaves_balance: 0,
      selected_plant_id: "bonsai-id",
      growth_points: 350,
      growth_stage: "BLOOMING",
      vitality: 45,
      catalog: [
        { id: "sunflower-id", species: "sunflower", name: "Sunflower", description: "", unlock_cost: 0, is_unlocked: true, is_selected: false },
        { id: "bonsai-id", species: "bonsai", name: "Bonsai", description: "", unlock_cost: 0, is_unlocked: true, is_selected: true },
      ],
    };
    expect(selectedPlantPresentation(garden)).toEqual({ species: "bonsai", frameIndex: 10, scale: 1 });
  });

  it("returns a safe fallback for unknown species", () => {
    const garden = {
      water_balance: 0,
      leaves_balance: 0,
      selected_plant_id: "unknown",
      growth_points: 0,
      growth_stage: "SPROUTING",
      vitality: 100,
      catalog: [{ id: "unknown", species: "fern", name: "Fern", description: "", unlock_cost: 0, is_unlocked: true, is_selected: true }],
    } satisfies GardenState;
    expect(selectedPlantPresentation(garden)).toBeNull();
  });

  it("falls back safely for unknown growth and vitality values", () => {
    expect(getPlantFrame("monstera", "UNKNOWN" as GrowthStage, Number.NaN)).toBe(3);
  });
});
