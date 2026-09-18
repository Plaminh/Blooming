<script lang="ts">
  import "../../styles/widget-theme.css";
  import type { CompanionWidgetProps } from "../../types/presentation";
  import {
    desktopWindowService,
    type DesktopWindowService,
  } from "$lib/platform/desktopWindow";
  import { actionsFor } from "../../model/actions";
  import { widgetLayoutStyle } from "../../model/layout";
  import WidgetSceneBackground from "../molecules/WidgetSceneBackground.svelte";
  import ScheduleAlerts from "../atoms/ScheduleAlerts.svelte";
  import ReminderAlerts from "../atoms/ReminderAlerts.svelte";
  import OfflineStatus from "../atoms/OfflineStatus.svelte";
  import MrBloomCharacter from "../atoms/MrBloomCharacter.svelte";
  import PixelStatus from "../atoms/PixelStatus.svelte";
  import PlantSprite from "../atoms/PlantSprite.svelte";
  import TimerDisplay from "../atoms/TimerDisplay.svelte";
  import WidgetTitleBar from "../molecules/WidgetTitleBar.svelte";
  import SpeechBubble from "../molecules/SpeechBubble.svelte";
  import ReminderPanel from "../molecules/ReminderPanel.svelte";
  import ActionGroup from "../molecules/ActionGroup.svelte";

  let {
    presentation,
    windowService = desktopWindowService,
    weather = "CLEAR",
    timezone = Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC",
    rainEnabled = true,
  }: CompanionWidgetProps & { windowService?: DesktopWindowService } = $props();

  function openMainOnDoubleClick(node: HTMLElement) {
    const handleDoubleClick = (event: MouseEvent) => {
      const target = event.target;
      if (
        target instanceof Element &&
        target.closest(
          'button, input, a, header, [role="button"], [data-no-open-main]',
        )
      ) {
        return;
      }
      void windowService.openMainWindow();
    };

    node.addEventListener("dblclick", handleDoubleClick);
    return {
      destroy() {
        node.removeEventListener("dblclick", handleDoubleClick);
      },
    };
  }

  let actions = $derived(actionsFor(presentation));
  let timeText = $derived(
    presentation.kind === "focusing" ||
      presentation.kind === "ending" ||
      presentation.kind === "paused" ||
      presentation.kind === "offline"
      ? presentation.timeText
      : undefined,
  );
  let speechText = $derived(
    presentation.kind === "ending" ||
      presentation.kind === "paused" ||
      presentation.kind === "behindSchedule" ||
      presentation.kind === "offline"
      ? presentation.speechText
      : undefined,
  );
</script>

<section
  use:openMainOnDoubleClick
  class="companion-widget state-{presentation.kind}"
  aria-label="Blooming companion"
  style={widgetLayoutStyle(presentation.kind)}
>
  <WidgetSceneBackground {weather} {timezone} {rainEnabled} />
  <WidgetTitleBar {windowService} />

  <div class="plant-slot">
    {#if presentation.activePlant}
      <PlantSprite plant={presentation.activePlant} />
    {:else}
      <span role="status">Plant unavailable</span>
    {/if}
  </div>

  <div class="character-anchor">
    <MrBloomCharacter kind={presentation.kind} />
    {#if presentation.kind === "behindSchedule"}
      <PixelStatus class="alert" label="Behind schedule">
        <ScheduleAlerts />
      </PixelStatus>
    {:else if presentation.kind === "reminders"}
      <PixelStatus class="alert" label="Reminder alerts">
        <ReminderAlerts />
      </PixelStatus>
    {:else if presentation.kind === "offline"}
      <PixelStatus class="offline" label="Offline">
        <OfflineStatus />
      </PixelStatus>
    {/if}
  </div>

  <div class="panel-slot">
    {#if presentation.kind === "reminders"}
      <ReminderPanel reminders={presentation.reminders} />
    {:else if speechText}
      <SpeechBubble text={speechText} kind={presentation.kind} />
    {/if}
  </div>

  {#if timeText}
    <div class="timer-slot">
      <TimerDisplay value={timeText} />
    </div>
  {/if}

  <div class="action-slot">
    <ActionGroup {actions} />
  </div>
</section>

<style>
  .character-anchor {
    position: absolute;
    left: var(--widget-character-left);
    bottom: var(--widget-character-bottom);
    z-index: 2;
    width: 220px;
    height: 188px;
  }

  .plant-slot {
    position: absolute;
    left: var(--widget-plant-left);
    bottom: var(--widget-plant-bottom);
    z-index: 1;
  }

  .character-anchor :global(.character) {
    position: absolute;
    left: 0;
    bottom: 0;
  }

  .character-anchor :global(.status) {
    position: absolute;
    top: var(--widget-status-top);
    left: var(--widget-status-left);
  }

  .panel-slot {
    position: absolute;
    top: var(--widget-panel-top);
    left: var(--widget-panel-left);
    z-index: 2;
    width: var(--widget-panel-width);
    height: var(--widget-panel-height);
  }

  .timer-slot {
    position: absolute;
    top: var(--widget-timer-top);
    right: var(--widget-timer-right);
    z-index: 2;
  }

  .action-slot {
    position: absolute;
    top: var(--widget-action-top);
    right: var(--widget-action-right);
    z-index: 2;
  }
</style>
