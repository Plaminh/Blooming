<script lang="ts">
  import { page } from "$app/state";
  import { CompanionWidget } from "$lib/features/companion-widget";
  import type {
    CompanionWidgetKind,
    CompanionWidgetPresentation,
    PlantSpecies,
  } from "$lib/features/companion-widget";
  import {
    behindScheduleFixture,
    offlineFixture,
    pausedFixture,
    remindersFixture,
    focusingFixture,
    endingFixture
  } from "$lib/features/companion-widget/fixtures";
  import {
    PLANT_SPECIES,
    clampPlantFrameIndex,
  } from "$lib/features/companion-widget/model/plants";

  const fixtures: Record<CompanionWidgetKind, CompanionWidgetPresentation> = {
    paused: pausedFixture,
    behindSchedule: behindScheduleFixture,
    offline: offlineFixture,
    reminders: remindersFixture,
    focusing: focusingFixture,
    ending: endingFixture,
  };

  const options: { kind: CompanionWidgetKind; label: string }[] = [
    { kind: "focusing", label: "Focusing" },
    { kind: "ending", label: "Ending" },
    { kind: "paused", label: "Paused" },
    { kind: "behindSchedule", label: "Behind schedule" },
    { kind: "offline", label: "Offline" },
    { kind: "reminders", label: "Reminders" },
  ];

  function asKind(value: string | null): CompanionWidgetKind {
    if (
      value === "focusing" ||
      value === "ending" ||
      value === "paused" ||
      value === "behindSchedule" ||
      value === "offline" ||
      value === "reminders"
    ) {
      return value;
    }
    return "focusing";
  }

  function asSpecies(value: string | null): PlantSpecies {
    return PLANT_SPECIES.find((species) => species === value) ?? "monstera";
  }

  function asNumber(value: string | null, fallback: number): number {
    if (value === null || value.trim() === "") return fallback;
    const parsed = Number(value);
    return Number.isFinite(parsed) ? parsed : fallback;
  }

  let kind = $state<CompanionWidgetKind>(asKind(page.url.searchParams.get("kind")));
  let species = $state<PlantSpecies>(
    asSpecies(page.url.searchParams.get("plant")),
  );
  let frame = $state(asNumber(page.url.searchParams.get("frame"), 7));
  let presentation = $derived<CompanionWidgetPresentation>({
    ...fixtures[kind],
    activePlant: {
      species,
      frameIndex: clampPlantFrameIndex(frame),
    },
  });
  let shot = $derived(page.url.searchParams.get("shot") === "1");
</script>

<main class="preview" class:shot>
  <p class="hint">Development preview — selector is outside the widget.</p>
  <div class="controls">
    <div class="selector" role="group" aria-label="Widget fixture">
      {#each options as option (option.kind)}
        <button
          type="button"
          class:active={kind === option.kind}
          onclick={() => {
            kind = option.kind;
          }}
        >
          {option.label}
        </button>
      {/each}
    </div>

    <div class="asset-controls">
      <label>
        Plant
        <select bind:value={species}>
          {#each PLANT_SPECIES as option (option)}
            <option value={option}>{option}</option>
          {/each}
        </select>
      </label>

      <label>
        Lifecycle frame
        <select bind:value={frame}>
          {#each Array.from({ length: 16 }, (_, index) => index) as option (option)}
            <option value={option}>{option}</option>
          {/each}
        </select>
      </label>

    </div>
  </div>
  <div class="frame">
    <CompanionWidget {presentation} />
  </div>
</main>

<style>
  .preview {
    min-height: 100vh;
    padding: 24px;
    background: #1a1a1a;
    color: #f4f4f5;
  }

  .hint {
    margin: 0 0 12px;
    font-size: 14px;
  }

  .selector {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .selector button {
    padding: 6px 12px;
    border: 1px solid #52525b;
    border-radius: 6px;
    background: #27272a;
    color: inherit;
    cursor: pointer;
  }

  .selector button.active {
    background: #3f3f46;
    border-color: #a1a1aa;
  }

  .controls {
    display: grid;
    gap: 10px;
    margin-bottom: 16px;
  }

  .asset-controls {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
  }

  .asset-controls label {
    display: grid;
    gap: 4px;
    font-size: 12px;
    font-weight: 700;
  }

  .asset-controls select {
    min-width: 140px;
    padding: 6px 8px;
    border: 1px solid #52525b;
    border-radius: 5px;
    background: #27272a;
    color: inherit;
  }

  .frame {
    width: 680px;
    height: 289px;
  }

  .shot {
    min-height: 289px;
    padding: 0;
    background: transparent;
  }

  .shot .hint,
  .shot .controls {
    display: none;
  }
</style>
