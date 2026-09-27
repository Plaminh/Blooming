import { render } from "@testing-library/svelte";
import { afterEach, describe, expect, it, vi } from "vitest";
import WateringSprite from "./WateringSprite.svelte";
import { WATERING_ATLAS } from "$lib/features/companion-widget/model/plants";

describe("WateringSprite", () => {
  afterEach(() => vi.useRealTimers());

  it("plays all eight frames once and completes once", async () => {
    vi.useFakeTimers();
    const onComplete = vi.fn();
    const { container, unmount } = render(WateringSprite, { onComplete });

    expect(container.querySelector("img")).toHaveAttribute("src", WATERING_ATLAS.src);
    expect(container.querySelector(".watering-sprite")).toHaveAttribute("data-frame", "0");
    await vi.advanceTimersByTimeAsync(WATERING_ATLAS.frameDurationMs * WATERING_ATLAS.frameCount);
    expect(container.querySelector(".watering-sprite")).toHaveAttribute("data-frame", "7");
    expect(onComplete).toHaveBeenCalledTimes(1);
    await vi.advanceTimersByTimeAsync(WATERING_ATLAS.frameDurationMs * 2);
    expect(onComplete).toHaveBeenCalledTimes(1);
    unmount();
  });

  it("cancels its timer when unmounted", async () => {
    vi.useFakeTimers();
    const onComplete = vi.fn();
    const { unmount } = render(WateringSprite, { onComplete });
    unmount();
    await vi.runAllTimersAsync();
    expect(onComplete).not.toHaveBeenCalled();
  });
});
