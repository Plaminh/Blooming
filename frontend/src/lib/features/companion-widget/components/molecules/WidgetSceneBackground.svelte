<script lang="ts">
  import { WIDGET_SCENE } from "../../model/atlas";
  import {
    type Daytime,
    type Season,
    type Weather,
    getDaytimeFromHour,
    datePartsInTimezone,
    DAYTIME_ASSETS,
    SEASON_ASSETS,
    WEATHER_ASSETS
  } from "../../model/environment";
  import RainLayer from "../atoms/RainLayer.svelte";
  import { clockStore } from "$lib/shared/stores/clockStore";
  import { environmentStore } from "$lib/shared/stores/environmentStore";
  import { deviceTimezone } from '$lib/shared/deviceLocation';
  import { resolveSeason } from '$lib/shared/utils/season';

  type Props = {
    class?: string;
    variant?: "widget" | "garden";
    weatherCondition?: Weather;
    weatherOverride?: Weather;
    seasonOverride?: Season;
    daytimeOverride?: Daytime;
    timezoneOverride?: string;
    animationOverride?: boolean;
  };

  let { 
    class: className = "", 
    variant = "widget",
    weatherCondition,
    weatherOverride,
    seasonOverride,
    daytimeOverride,
    timezoneOverride,
    animationOverride
  }: Props = $props();
  
  let timezone = $derived(timezoneOverride || $environmentStore.effectiveTimezone || deviceTimezone());
  let rainEnabled = $derived(animationOverride ?? ($environmentStore.animationEnabled !== false));
  
  // Use overrides if provided, else use environment store
  let weather = $derived(weatherOverride ?? weatherCondition ?? ($environmentStore.weatherCondition as Weather));

  let zonedTime = $derived(datePartsInTimezone($clockStore, timezone));
  let currentDaytime: Daytime = $derived(daytimeOverride || getDaytimeFromHour(zonedTime.hour));
  let currentSeason: Season = $derived(seasonOverride || ($environmentStore.sceneSeason === 'AUTO'
    ? resolveSeason('AUTO', zonedTime.month, null) as Season
    : ($environmentStore.sceneSeason as Season)));
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
    <RainLayer {weather} enabled={rainEnabled} widgetHidden={variant === 'widget' && $environmentStore.widgetVisible === false} />
  </div>
  {#if !weatherOverride && $environmentStore.weatherStatus === 'STALE' && weather !== 'CLEAR'}
    <div class="stale-indicator" aria-label="Weather data is stale" title="Weather data might be outdated">↻</div>
  {/if}
</div>

<style>
  .stale-indicator {
    position: absolute;
    top: 6px;
    right: 6px;
    color: rgba(255, 255, 255, 0.7);
    z-index: 10;
    pointer-events: auto;
  }

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

  .scene--garden::after {
    bottom: 0;
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
    /* Cover either garden viewport with the same 680 x 235 visible crop
       used by the widget. Wider or taller panels crop the excess. */
    --garden-frame-width: max(100cqw, calc(680 / 235 * 100cqh));
    left: 50%;
    bottom: calc(-40 / 680 * var(--garden-frame-width));
    width: var(--garden-frame-width);
    height: calc(837 / 1880 * var(--garden-frame-width));
    transform: translateX(-50%);
  }

  .scene--garden .sky,
  .scene--garden .bushes,
  .scene--garden .weather-overlay {
    width: 100%;
    height: 100%;
  }

  .scene--garden .bushes {
    bottom: calc(-65 / 1880 * var(--garden-frame-width));
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
