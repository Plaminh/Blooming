<script lang="ts">
  type Props = {
    value: string;
    class?: string;
  };

  let { value, class: className = "" }: Props = $props();
</script>

<p class="timer {className}">{value}</p>

<style>
  .timer {
    margin: 0;
    color: #f8f5e9;
    font-family: var(--widget-font, monospace);
    font-size: 64px;
    font-weight: 900;
    font-variant-numeric: tabular-nums;
    letter-spacing: -0.09em;
    line-height: 1;
    -webkit-text-stroke: 2px var(--widget-navy, #0e3052);
    paint-order: stroke fill;
    text-shadow:
      2px 2px 0 var(--widget-navy, #0e3052),
      -2px 2px 0 var(--widget-navy, #0e3052),
      2px -2px 0 var(--widget-navy, #0e3052),
      -2px -2px 0 var(--widget-navy, #0e3052);
  }
</style>
