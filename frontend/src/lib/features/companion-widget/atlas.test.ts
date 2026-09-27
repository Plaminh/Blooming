import { render } from "@testing-library/svelte";
import { tick } from "svelte";
import { afterEach, describe, expect, it, vi } from "vitest";
import MrBloomCharacter from "./components/atoms/MrBloomCharacter.svelte";
import {
  MR_BLOOM_ATLAS,
  MR_BLOOM_FRAME_SEQUENCE,
  MR_BLOOM_ROWS,
  atlasCellForKind,
  atlasCellOffset,
  atlasFrameColumn,
  atlasSheetTransform,
} from "./model/atlas";

function mockReducedMotion(reduce: boolean) {
  vi.stubGlobal("matchMedia", (query: string) => ({
    matches: reduce && query.includes("prefers-reduced-motion"),
    media: query,
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    addListener: vi.fn(),
    removeListener: vi.fn(),
    dispatchEvent: vi.fn(),
  }));
}

describe("Mr. Bloom normalized atlas", () => {
  afterEach(() => {
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  it("maps every state to its inspected row and permitted frame sequence", () => {
    expect(MR_BLOOM_ROWS).toEqual({
      focusing: 3,
      ending: 4,
      paused: 7,
      behindSchedule: 6,
      offline: 3,
      reminders: 4,
    });
    expect(MR_BLOOM_FRAME_SEQUENCE).toEqual({
      focusing: [0, 1, 2, 3],
      ending: [0, 1],
      paused: [0, 1, 2, 3],
      behindSchedule: [0, 2],
      offline: [0, 1, 2, 3],
      reminders: [1],
    });
    expect(atlasCellForKind("paused", 1)).toEqual({ col: 1, row: 7 });
    expect(atlasCellForKind("behindSchedule", 1)).toEqual({ col: 2, row: 6 });
    expect(atlasCellForKind("offline", 3)).toEqual({ col: 3, row: 3 });
    expect(atlasCellForKind("reminders", 20)).toEqual({ col: 1, row: 4 });
    expect(atlasFrameColumn("paused", Number.NaN)).toBe(0);
  });

  it("uses a 1152 × 1152 sheet with 4 × 8 cells of 288 × 144", () => {
    expect(MR_BLOOM_ATLAS).toMatchObject({
      sheetWidth: 1152,
      sheetHeight: 1152,
      columns: 4,
      rows: 8,
      cellWidth: 288,
      cellHeight: 144,
    });
    expect(MR_BLOOM_ATLAS.columns * MR_BLOOM_ATLAS.cellWidth).toBe(MR_BLOOM_ATLAS.sheetWidth);
    expect(MR_BLOOM_ATLAS.rows * MR_BLOOM_ATLAS.cellHeight).toBe(MR_BLOOM_ATLAS.sheetHeight);
    expect(atlasCellOffset({ col: 2, row: 4 })).toEqual({ x: 576, y: 576 });
    expect(atlasSheetTransform({ col: 2, row: 4 }, 0.5)).toBe(
      "scale(0.5) translate(-576px, -576px)",
    );
  });

  it("clips exactly one normalized cell at a 110px rendered height", () => {
    const { container } = render(MrBloomCharacter, { props: { kind: "paused" } });
    const character = container.querySelector(".character") as HTMLElement;
    const viewport = container.querySelector(".viewport") as HTMLElement;
    const sheet = container.querySelector(".sheet") as HTMLImageElement;

    expect(container.querySelectorAll(".character")).toHaveLength(1);
    expect(getComputedStyle(viewport).overflow).toBe("hidden");
    expect(character.style.getPropertyValue("--display-w")).toBe("220px");
    expect(character.style.getPropertyValue("--display-h")).toBe("110px");
    expect(sheet).toHaveAttribute("src", MR_BLOOM_ATLAS.src);
    expect(sheet).toHaveAttribute("width", "1152");
    expect(sheet).toHaveAttribute("height", "1152");
    expect(MR_BLOOM_ATLAS.src).toBe("/assets/mr-bloom/mr-bloom-spritesheet.png");
  });

  it("cycles through all four paused columns and resets when kind changes", async () => {
    vi.useFakeTimers();
    mockReducedMotion(false);
    const { container, rerender } = render(MrBloomCharacter, { props: { kind: "paused" } });
    const character = () => container.querySelector(".character") as HTMLElement;
    await tick();

    expect(character()).toHaveAttribute("data-frame", "0");
    await vi.advanceTimersByTimeAsync(MR_BLOOM_ATLAS.frameIntervalMs);
    expect(character()).toHaveAttribute("data-frame", "1");
    await vi.advanceTimersByTimeAsync(MR_BLOOM_ATLAS.frameIntervalMs);
    expect(character()).toHaveAttribute("data-frame", "2");
    await vi.advanceTimersByTimeAsync(MR_BLOOM_ATLAS.frameIntervalMs);
    expect(character()).toHaveAttribute("data-frame", "3");
    await vi.advanceTimersByTimeAsync(MR_BLOOM_ATLAS.frameIntervalMs);
    expect(character()).toHaveAttribute("data-frame", "0");

    await rerender({ kind: "reminders" });
    await tick();
    expect(character()).toHaveAttribute("data-row", "4");
    expect(character()).toHaveAttribute("data-frame", "1");
    expect(character()).toHaveAttribute("data-sequence-index", "0");
  });

  it("cleans up an active animation timer on destroy", async () => {
    vi.useFakeTimers();
    mockReducedMotion(false);
    const clearSpy = vi.spyOn(window, "clearInterval");
    const { unmount } = render(MrBloomCharacter, { props: { kind: "offline" } });
    await tick();
    unmount();
    expect(clearSpy).toHaveBeenCalled();
  });

  it("freezes on the first permitted frame for reduced motion", async () => {
    vi.useFakeTimers();
    mockReducedMotion(true);
    const { container } = render(MrBloomCharacter, { props: { kind: "behindSchedule" } });
    const character = container.querySelector(".character") as HTMLElement;
    await tick();

    expect(character).toHaveAttribute("data-frame", "0");
    await vi.advanceTimersByTimeAsync(MR_BLOOM_ATLAS.frameIntervalMs * 4);
    expect(character).toHaveAttribute("data-frame", "0");
  });
});
