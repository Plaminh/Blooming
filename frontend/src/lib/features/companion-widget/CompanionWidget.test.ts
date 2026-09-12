import { render, screen } from "@testing-library/svelte";
import userEvent from "@testing-library/user-event";
import axe from "axe-core";
import { describe, expect, it, vi } from "vitest";
import CompanionWidget from "./components/organisms/CompanionWidget.svelte";
import {
  DEFAULT_WIDGET_SCENE,
  behindScheduleFixture,
  offlineFixture,
  pausedFixture,
  remindersFixture,
} from "./fixtures";
import type { CompanionWidgetPresentation } from "./types/presentation";
import { WIDGET_SCENE } from "./model/atlas";
import { WIDGET_LAYOUTS, MR_BLOOM_POSITION, PANEL_POSITION } from "./model/layout";

const fixtures: CompanionWidgetPresentation[] = [
  pausedFixture,
  behindScheduleFixture,
  offlineFixture,
  remindersFixture,
];

function follows(first: Element, second: Element): boolean {
  return Boolean(first.compareDocumentPosition(second) & Node.DOCUMENT_POSITION_FOLLOWING);
}

describe("CompanionWidget", () => {
  it("uses the supplied leaf PNG only as the decorative title logo", () => {
    const { container } = render(CompanionWidget, { props: { presentation: pausedFixture } });
    const logo = container.querySelector(".logo img") as HTMLImageElement;

    expect(logo).toHaveAttribute("src", "/assets/widget/icons/leaf-icon.png");
    expect(logo).toHaveAttribute("alt", "");
    expect(container.querySelector(".leaf-balance")).not.toBeInTheDocument();
    expect(container.textContent).not.toContain("125");
    expect(container.querySelectorAll(".character")).toHaveLength(1);
    expect(container.querySelectorAll(".plant")).toHaveLength(1);
  });

  it("renders exactly one character and one selected plant", () => {
    const { container } = render(CompanionWidget, { props: { presentation: pausedFixture } });
    expect(container.querySelectorAll(".character")).toHaveLength(1);
    expect(container.querySelectorAll(".plant")).toHaveLength(1);
  });

  it("renders paused copy and invokes both provided callbacks", async () => {
    const user = userEvent.setup();
    const onResume = vi.fn();
    const onEnd = vi.fn();
    render(CompanionWidget, {
      props: {
        presentation: { ...pausedFixture, onResume, onEnd },
      },
    });

    expect(screen.getByText("Paused. Take your time.")).toBeInTheDocument();
    expect(screen.getByText("18:42")).toBeInTheDocument();
    expect(screen.queryByLabelText("Sleeping")).not.toBeInTheDocument();
    expect(document.querySelector(".sleep-z")).not.toBeInTheDocument();

    const resume = screen.getByRole("button", { name: /resume/i });
    const end = screen.getByRole("button", { name: /end/i });
    expect(follows(resume, end)).toBe(true);

    await user.click(resume);
    await user.click(end);
    expect(onResume).toHaveBeenCalledTimes(1);
    expect(onEnd).toHaveBeenCalledTimes(1);
  });

  it("omits the timer when paused timeText is missing", () => {
    render(CompanionWidget, {
      props: {
        presentation: {
          ...DEFAULT_WIDGET_SCENE,
          kind: "paused",
          speechText: "Paused. Take your time.",
        },
      },
    });

    expect(screen.getByText("Paused. Take your time.")).toBeInTheDocument();
    expect(screen.queryByText("18:42")).not.toBeInTheDocument();
  });

  it("renders behind-schedule copy, alert status, no timer, and REPLAN / LATER / OPEN", async () => {
    const user = userEvent.setup();
    const onReplan = vi.fn();
    const onLater = vi.fn();
    const onOpen = vi.fn();
    render(CompanionWidget, {
      props: {
        presentation: { ...behindScheduleFixture, onReplan, onLater, onOpen },
      },
    });

    expect(
      screen.getByText("We are 35 minutes behind. Adjust the remaining plan?"),
    ).toBeInTheDocument();
    expect(screen.getByLabelText("Behind schedule")).toBeInTheDocument();
    expect(screen.queryByText(/^\d{2}:\d{2}$/)).not.toBeInTheDocument();

    const replan = screen.getByRole("button", { name: /replan/i });
    const later = screen.getByRole("button", { name: /later/i });
    const open = screen.getByRole("button", { name: /open/i });
    expect(follows(replan, later)).toBe(true);
    expect(follows(later, open)).toBe(true);

    await user.click(replan);
    await user.click(later);
    await user.click(open);
    expect(onReplan).toHaveBeenCalledTimes(1);
    expect(onLater).toHaveBeenCalledTimes(1);
    expect(onOpen).toHaveBeenCalledTimes(1);
  });

  it("renders offline copy, time, status, and no action buttons", () => {
    render(CompanionWidget, {
      props: { presentation: offlineFixture },
    });

    expect(screen.getByText("Offline – changes will sync later.")).toBeInTheDocument();
    expect(screen.getByText("14:06")).toBeInTheDocument();
    expect(screen.getByLabelText("Offline")).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: /resume|end|replan|later|open|view|dismiss/i }),
    ).not.toBeInTheDocument();
  });

  it("renders reminders heading, items, and VIEW then DISMISS", async () => {
    const user = userEvent.setup();
    const onView = vi.fn();
    const onDismiss = vi.fn();
    render(CompanionWidget, {
      props: {
        presentation: { ...remindersFixture, onView, onDismiss },
      },
    });

    expect(screen.getByRole("heading", { name: "2 REMINDERS" })).toBeInTheDocument();
    expect(screen.getByText("Start Database")).toBeInTheDocument();
    expect(screen.getByText("Review milestone")).toBeInTheDocument();
    expect(screen.getByLabelText("Reminder alerts")).toBeInTheDocument();

    const view = screen.getByRole("button", { name: /view/i });
    const dismiss = screen.getByRole("button", { name: /dismiss/i });
    expect(follows(view, dismiss)).toBe(true);

    await user.click(view);
    await user.click(dismiss);
    expect(onView).toHaveBeenCalledTimes(1);
    expect(onDismiss).toHaveBeenCalledTimes(1);
  });

  it("keeps the full reminder label readable when the line is visually truncated", () => {
    const label = "Start Database with a very long milestone label";
    render(CompanionWidget, {
      props: {
        presentation: {
          ...DEFAULT_WIDGET_SCENE,
          kind: "reminders",
          reminders: [{ id: "long", label }],
        },
      },
    });

    expect(screen.getByText(label)).toBeInTheDocument();
    expect(screen.getByRole("listitem")).toHaveTextContent(label);
    expect(screen.getByRole("listitem")).toHaveAttribute("title", label);
    expect(screen.getByRole("heading", { name: "1 REMINDER" })).toBeInTheDocument();
  });

  it("keeps every action visible and inert when its callback is omitted", async () => {
    const user = userEvent.setup();
    const callbackFree: { presentation: CompanionWidgetPresentation; labels: string[] }[] = [
      {
        presentation: {
          ...DEFAULT_WIDGET_SCENE,
          kind: "paused",
          speechText: pausedFixture.speechText,
          timeText: pausedFixture.timeText,
        },
        labels: ["RESUME", "END"],
      },
      {
        presentation: {
          ...DEFAULT_WIDGET_SCENE,
          kind: "behindSchedule",
          speechText: behindScheduleFixture.speechText,
        },
        labels: ["REPLAN", "LATER", "OPEN"],
      },
      {
        presentation: {
          ...DEFAULT_WIDGET_SCENE,
          kind: "reminders",
          reminders: remindersFixture.reminders,
        },
        labels: ["VIEW", "DISMISS"],
      },
    ];

    for (const { presentation, labels } of callbackFree) {
      const { unmount } = render(CompanionWidget, { props: { presentation } });

      for (const label of labels) {
        await user.click(screen.getByRole("button", { name: label }));
        expect(screen.getByRole("button", { name: label })).toBeInTheDocument();
      }
      unmount();
    }
  });

  it("activates paused actions from the keyboard", async () => {
    const user = userEvent.setup();
    const onResume = vi.fn();
    render(CompanionWidget, {
      props: {
        presentation: { ...pausedFixture, onResume },
      },
    });

    const resume = screen.getByRole("button", { name: /resume/i });
    resume.focus();
    expect(resume).toHaveFocus();
    await user.keyboard("{Enter}");
    expect(onResume).toHaveBeenCalledTimes(1);
  });

  it("keeps window controls operable when Tauri APIs are unavailable", async () => {
    const user = userEvent.setup();
    render(CompanionWidget, {
      props: { presentation: pausedFixture },
    });

    for (const name of ["Minimize", "Maximize or restore", "Close"]) {
      const control = screen.getByRole("button", { name });
      expect(control).toBeInTheDocument();
      await user.click(control);
      expect(control).toBeInTheDocument();
    }
  });

  it("uses the shared 1880×837 bottom-left scene box", () => {
    const { container } = render(CompanionWidget, {
      props: { presentation: pausedFixture },
    });

    const frame = container.querySelector(".frame") as HTMLElement;
    expect(frame).toBeInTheDocument();

    // The frame inherits the sky-sized box, so both layers scale as one unit.
    const framed = getComputedStyle(frame);
    expect(framed.getPropertyValue("--frame-w").trim()).toBe(`${WIDGET_SCENE.frameWidth}px`);
    expect(framed.getPropertyValue("--frame-h").trim()).toBe(`${WIDGET_SCENE.frameHeight}px`);

    const sky = container.querySelector(".sky") as HTMLImageElement;
    const bushes = container.querySelector(".bushes") as HTMLImageElement;
    expect(sky).toHaveAttribute("width", String(WIDGET_SCENE.frameWidth));
    expect(sky).toHaveAttribute("height", String(WIDGET_SCENE.frameHeight));
    expect(bushes).toHaveAttribute("width", String(WIDGET_SCENE.bushesWidth));
    expect(bushes).toHaveAttribute("height", String(WIDGET_SCENE.bushesHeight));
    expect(getComputedStyle(sky).bottom).toBe(getComputedStyle(bushes).bottom);
    expect(getComputedStyle(sky).left).toBe(getComputedStyle(bushes).left);
    expect(WIDGET_SCENE.anchor).toBe("bottom-left");
  });

  it("drives each state from its own layout configuration", () => {
    for (const presentation of fixtures) {
      const { container, unmount } = render(CompanionWidget, { props: { presentation } });
      const widget = container.querySelector(".companion-widget") as HTMLElement;
      const layout = WIDGET_LAYOUTS[presentation.kind];

      expect(widget.style.getPropertyValue("--widget-panel-left")).toBe(`${layout.panel.x}px`);
      expect(widget.style.getPropertyValue("--widget-panel-top")).toBe(`${layout.panel.y}px`);
      expect(widget.style.getPropertyValue("--widget-panel-width")).toBe(`${layout.panel.width}px`);
      expect(widget.style.getPropertyValue("--widget-panel-height")).toBe(
        `${layout.panel.height}px`,
      );
      expect(widget.style.getPropertyValue("--widget-character-left")).toBe(
        `${layout.character.left}px`,
      );
      expect(widget.style.getPropertyValue("--widget-plant-left")).toBe(`${layout.plant.left}px`);
      unmount();
    }

    // All states must share the same character position and top-left panel position
    for (const kind of ["paused", "behindSchedule", "offline", "reminders"] as const) {
      const layout = WIDGET_LAYOUTS[kind];
      expect(layout.character.left).toBe(MR_BLOOM_POSITION.left);
      expect(layout.character.bottom).toBe(MR_BLOOM_POSITION.bottom);
      expect(layout.panel.x).toBe(PANEL_POSITION.x);
      expect(layout.panel.y).toBe(PANEL_POSITION.y);
    }

    // Panel dimensions remain state-specific
    expect(WIDGET_LAYOUTS.paused.panel).toEqual(expect.objectContaining({ width: 250, height: 86 }));
    expect(WIDGET_LAYOUTS.behindSchedule.panel).toEqual(expect.objectContaining({ width: 366, height: 90 }));
    expect(WIDGET_LAYOUTS.offline.panel).toEqual(expect.objectContaining({ width: 252, height: 111 }));
    expect(WIDGET_LAYOUTS.reminders.panel).toEqual(expect.objectContaining({ width: 328, height: 128 }));

    // Status overlays remain state-specific
    expect(WIDGET_LAYOUTS.paused.character.status).toEqual({ x: 90, y: 36 });
    expect(WIDGET_LAYOUTS.behindSchedule.character.status).toEqual({ x: 168, y: 76 });
    expect(WIDGET_LAYOUTS.offline.character.status).toEqual({ x: 163, y: 70 });
    expect(WIDGET_LAYOUTS.reminders.character.status).toEqual({ x: 172, y: 79 });

    expect(WIDGET_LAYOUTS.behindSchedule.timer).toBeUndefined();
    expect(WIDGET_LAYOUTS.paused.timer).toBeDefined();
    expect(WIDGET_LAYOUTS.offline.timer).toBeDefined();
  });

  it.each(fixtures)("has no axe-core violations in the $kind fixture", async (presentation) => {
    const { container } = render(CompanionWidget, { props: { presentation } });
    const results = await axe.run(container);
    expect(results.violations).toEqual([]);
  });
});
