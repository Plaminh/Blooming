import { render } from "@testing-library/svelte";
import { describe, expect, it } from "vitest";
import CompanionWidget from "./components/organisms/CompanionWidget.svelte";
import PlantSprite from "./components/atoms/PlantSprite.svelte";
import { pausedFixture } from "./fixtures";
import {
  PLANT_ATLAS,
  PLANT_SOURCES,
  PLANT_SPECIES,
  clampPlantFrameIndex,
  plantCellForFrame,
  plantSheetTransform,
  plantSource,
} from "./model/plants";
import { WIDGET_LAYOUTS } from "./model/layout";

describe("plant presentation", () => {
  it("resolves every species to its runtime sprite sheet", () => {
    expect(PLANT_SPECIES).toEqual([
      "monstera",
      "sunflower",
      "bonsai",
      "jasmine",
      "lavender",
    ]);
    expect(plantSource("monstera")).toBe("/assets/widget/plants/monstera-spritesheet.png");
    expect(plantSource("jasmine")).toBe("/assets/widget/plants/jasmine-spritesheet.png");
    expect(Object.keys(PLANT_SOURCES)).toEqual([...PLANT_SPECIES]);
  });

  it("maps lifecycle frames 0 and 15 onto the 8 × 2 atlas", () => {
    expect(plantCellForFrame(0)).toEqual({ col: 0, row: 0 });
    expect(plantCellForFrame(7)).toEqual({ col: 7, row: 0 });
    expect(plantCellForFrame(8)).toEqual({ col: 0, row: 1 });
    expect(plantCellForFrame(15)).toEqual({ col: 7, row: 1 });
    expect(plantSheetTransform(0, 0.25)).toBe("scale(0.25) translate(0px, 0px)");
    expect(plantSheetTransform(15, 0.25)).toBe("scale(0.25) translate(-2016px, -448px)");
  });

  it("clamps invalid frame values to the 0–15 contract", () => {
    expect(clampPlantFrameIndex(-3)).toBe(0);
    expect(clampPlantFrameIndex(99)).toBe(15);
    expect(clampPlantFrameIndex(Number.NaN)).toBe(0);
    expect(plantCellForFrame(-1).col).toBe(0);
    expect(plantCellForFrame(32).col).toBe(7);
  });

  it("renders one clipped frame and does not autoplay", () => {
    const { container, rerender } = render(PlantSprite, {
      props: { plant: { species: "lavender", frameIndex: 0 } },
    });
    const plant = container.querySelector(".plant") as HTMLElement;
    const viewport = container.querySelector(".viewport") as HTMLElement;
    const sheet = container.querySelector(".sheet") as HTMLImageElement;

    expect(plant).toHaveAttribute("data-species", "lavender");
    expect(plant).toHaveAttribute("data-frame", "0");
    expect(plant).toHaveAttribute("aria-hidden", "true");
    expect(getComputedStyle(viewport).overflow).toBe("hidden");
    expect(sheet).toHaveAttribute("src", PLANT_SOURCES.lavender);
    expect(sheet.style.transform).toBe(
      plantSheetTransform(0, PLANT_ATLAS.displayHeight / PLANT_ATLAS.cellHeight),
    );

    rerender({ plant: { species: "lavender", frameIndex: 15 } });
    expect(plant).toHaveAttribute("data-frame", "15");
    expect(sheet.style.transform).toBe(
      plantSheetTransform(15, PLANT_ATLAS.displayHeight / PLANT_ATLAS.cellHeight),
    );
    expect(container.querySelectorAll(".plant")).toHaveLength(1);
  });

  it("shows only the selected plant inside the widget", () => {
    const { container, rerender } = render(CompanionWidget, {
      props: {
        presentation: {
          ...pausedFixture,
          activePlant: { species: "sunflower", frameIndex: 4 },
        },
      },
    });

    expect(container.querySelectorAll(".plant")).toHaveLength(1);
    expect(container.querySelector(".plant")).toHaveAttribute("data-species", "sunflower");
    expect(container.querySelector(".sheet[src*='sunflower']")).toBeInTheDocument();
    expect(container.querySelector(".sheet[src*='bonsai']")).not.toBeInTheDocument();

    rerender({
      presentation: {
        ...pausedFixture,
        activePlant: { species: "bonsai", frameIndex: 4 },
      },
    });
    expect(container.querySelectorAll(".plant")).toHaveLength(1);
    expect(container.querySelector(".plant")).toHaveAttribute("data-species", "bonsai");
  });

  it("uses the same far-left plant anchor in every state", () => {
    for (const layout of Object.values(WIDGET_LAYOUTS)) {
      expect(layout.plant).toEqual({ left: -4, bottom: 4 });
    }
  });
});
