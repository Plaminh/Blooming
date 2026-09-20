<script lang="ts">
  import { RAIN_CONFIGS, type Weather } from "../../model/environment";
  import { onMount } from 'svelte';

  type Props = {
    weather: Weather;
    enabled?: boolean;
    widgetHidden?: boolean;
  };

  let { weather, enabled = true, widgetHidden = false }: Props = $props();
  let reducedMotion = $state(false);
  let documentHidden = $state(false);

  onMount(() => {
    const media = typeof window.matchMedia === 'function'
      ? window.matchMedia('(prefers-reduced-motion: reduce)') : null;
    const updateMotion = () => { reducedMotion = media?.matches ?? false; };
    const updateVisibility = () => { documentHidden = document.hidden; };
    updateMotion();
    updateVisibility();
    media?.addEventListener('change', updateMotion);
    document.addEventListener('visibilitychange', updateVisibility);
    return () => {
      media?.removeEventListener('change', updateMotion);
      document.removeEventListener('visibilitychange', updateVisibility);
    };
  });

  type Streak = {
    x: number;
    yOffset: number;
    delay: number;
    duration: number;
    length: number;
  };

  // Deterministic random generator to avoid flicker on rerenders
  function pseudoRandom(seed: number) {
    const x = Math.sin(seed) * 10000;
    return x - Math.floor(x);
  }

  function generateStreaks(weatherMode: 'RAIN' | 'THUNDERSTORM'): Streak[] {
    const config = RAIN_CONFIGS[weatherMode];
    const streaks: Streak[] = [];
    for (let i = 0; i < config.streakCount; i++) {
      streaks.push({
        x: pseudoRandom(i * 10) * 100, // 0-100%
        yOffset: pseudoRandom(i * 10 + 1) * -100, // start above view
        delay: pseudoRandom(i * 10 + 2) * config.maxDurationMs, // Will be applied as negative delay
        duration: config.minDurationMs + pseudoRandom(i * 10 + 3) * (config.maxDurationMs - config.minDurationMs),
        length: 5 + pseudoRandom(i * 10 + 4) * 20, // 5px to 25px
      });
    }
    return streaks;
  }

  let mode = $derived((weather === 'THUNDERSTORM' || weather === 'RAIN') ? weather : null);
  let config = $derived(mode ? RAIN_CONFIGS[mode] : null);
  let streaks = $derived(mode ? generateStreaks(mode) : []);
</script>

{#if mode && enabled && !reducedMotion && !documentHidden && !widgetHidden}
  <div class="rain-layer" aria-hidden="true">
    {#each streaks as streak}
      <div
        class="streak"
        style:left="{streak.x}%"
        style:top="{streak.yOffset}px"
        style:height="{streak.length}px"
        style:background-color={config?.color}
        style:animation-duration="{streak.duration}ms"
        style:animation-delay="-{streak.delay}ms"
      ></div>
    {/each}
  </div>
{/if}

<style>
  .rain-layer {
    position: absolute;
    inset: 0;
    pointer-events: none;
    overflow: hidden;
    z-index: 4; /* Above weather overlay but below UI */
    container-type: size;
  }
  .streak {
    position: absolute;
    width: 2px;
    animation-name: fall;
    animation-timing-function: linear;
    animation-iteration-count: infinite;
    opacity: 0;
  }
  @keyframes fall {
    0% {
      transform: translate(0, -10cqh);
      opacity: 0;
    }
    10% {
      opacity: 1;
    }
    80% {
      opacity: 1;
    }
    100% {
      /* Slanted fall using translate instead of rotate to keep edges crisp */
      transform: translate(-15cqw, 110cqh);
      opacity: 0;
    }
  }
</style>
