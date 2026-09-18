<script lang="ts">
  import { WIDGET_SCENE } from "../../model/atlas";
  import {
    type Daytime,
    type Season,
    type Weather,
    getDaytimeFromHour,
    getSeasonFromMonth,
    datePartsInTimezone,
    DAYTIME_ASSETS,
    SEASON_ASSETS,
    WEATHER_ASSETS
  } from "../../model/environment";
  import RainLayer from "../atoms/RainLayer.svelte";
  import { clockStore } from "$lib/shared/stores/clockStore";

  type Props = {
    class?: string;
    variant?: "widget" | "garden";
    weather?: Weather;
    rainEnabled?: boolean;
    timezone?: string;
  };

  let { class: className = "", variant = "widget", weather = 'CLEAR', rainEnabled = true, timezone = Intl.DateTimeFormat().resolvedOptions().timeZone || 'UTC' }: Props = $props();

  let zonedTime = $derived(datePartsInTimezone($clockStore, timezone));
  let currentDaytime: Daytime = $derived(getDaytimeFromHour(zonedTime.hour));
  let currentSeason: Season = $derived(getSeasonFromMonth(zonedTime.month));
</script>

<div
  class="scene scene--{variant} {className}"
  aria-hidden="true"
  style:--frame-w="{WIDGET_SCENE.frameWidth}px"
  style:--frame-h="{WIDGET_SCENE.frameHeight}px"
  style:--bushes-w="{WIDGET_SCENE.bushesWidth}px"
  style:--bushes-h="{WIDGET_SCENE.bushesHeight}px"
  style:--bushes-offset-y="{WIDGET_SCENE.bushesOffsetY}px"
>
  <div class="frame">
    <!-- 1. Time Background -->
    <img class="sky" src={DAYTIME_ASSETS[currentDaytime]} alt="" width={WIDGET_SCENE.frameWidth} height={WIDGET_SCENE.frameHeight} />

    <!-- 2. Season Vegetation -->
    <img
      class="bushes"
      src={SEASON_ASSETS[currentSeason]}
      alt=""
      width={WIDGET_SCENE.bushesWidth}
      height={WIDGET_SCENE.bushesHeight}
    />

    <!-- 3. Weather Effect Overlay -->
    {#if WEATHER_ASSETS[weather]}
      <img
        class="weather-overlay"
        src={WEATHER_ASSETS[weather]}
        alt=""
        width={WIDGET_SCENE.frameWidth}
        height={WIDGET_SCENE.frameHeight}
      />
    {/if}

    <!-- 4. Rain Animation -->
    <RainLayer {weather} enabled={rainEnabled} />
  </div>
</div>

<style>
  .scene {
    position: absolute;
    inset: 0;
    overflow: hidden;
    pointer-events: none;
  }

  .scene::after {
    content: "";
    position: absolute;
    right: 0;
    bottom: 3px;
    left: 0;
    height: 13px;
    border-top: 3px solid #b59b71;
    background: #f0d9ac;
  }

  .frame {
    position: absolute;
    left: 0;
    bottom: -40px;
    width: var(--frame-w);
    height: var(--frame-h);
    overflow: hidden;
    transform-origin: left bottom;
    /* Keep both source layers on one coordinate system and shift the
       shared crop down to match the low foreground in the references. */
    transform: scale(0.361702128);
  }

  .scene--garden .frame {
    left: 50%;
    /* Scale the widget's 680 x 303 scene and -40px bottom offset to its
       235px visible area (289px widget minus 54px title bar). */
    bottom: calc(-40 / 235 * 100cqh);
    width: calc(680 / 235 * 100cqh);
    height: calc(303 / 235 * 100cqh);
    transform: translateX(-50%);
  }

  .scene--garden .sky,
  .scene--garden .bushes,
  .scene--garden .weather-overlay {
    width: auto;
    height: 100%;
  }

  .sky,
  .bushes,
  .weather-overlay {
    position: absolute;
    left: 0;
    bottom: 0;
    max-width: none;
    image-rendering: crisp-edges;
    image-rendering: pixelated;
  }

  .sky, .weather-overlay {
    width: var(--frame-w);
    height: var(--frame-h);
  }

  .weather-overlay {
    z-index: 3;
    pointer-events: none;
  }

  .bushes {
    width: var(--bushes-w);
    height: var(--bushes-h);
    z-index: 2;
  }

  .scene--widget .bushes {
    /* The seasonal sprites have transparent space below the tree row. */
    bottom: var(--bushes-offset-y);
  }
</style>
