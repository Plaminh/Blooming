<script lang="ts">
  type ControlKind = "minimize" | "maximize" | "close";

  type Props = {
    kind: ControlKind;
    label: string;
    onclick?: () => void;
  };

  let { kind, label, onclick }: Props = $props();
</script>

<button class="control {kind}" type="button" aria-label={label} {onclick}>
  {#if kind === "minimize"}
    <svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true" focusable="false">
      <rect x="3" y="11" width="10" height="2" fill="currentColor" />
    </svg>
  {:else if kind === "maximize"}
    <svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true" focusable="false">
      <rect x="3" y="3" width="10" height="10" fill="none" stroke="currentColor" stroke-width="2" />
    </svg>
  {:else}
    <svg width="16" height="16" viewBox="0 0 16 16" aria-hidden="true" focusable="false">
      <path d="M4 4 L12 12 M12 4 L4 12" stroke="currentColor" stroke-width="2" stroke-linecap="round" />
    </svg>
  {/if}
</button>

<style>
  .control {
    display: grid;
    place-items: center;
    margin: 0;
    padding: 0;
    border: 3px solid var(--widget-cream-stroke, #173754);
    border-radius: 0;
    background: var(--widget-cream, #faefd5);
    box-shadow: inset 0 -2px 0 #d6cbb1;
    color: var(--widget-cream-stroke, #173754);
    cursor: pointer;
    image-rendering: pixelated;
  }

  .control :global(svg) {
    width: 18px;
    height: 18px;
    shape-rendering: crispEdges;
  }

  .minimize {
    width: 35px;
    height: 33px;
  }

  .maximize {
    width: 33px;
    height: 33px;
  }

  .close {
    width: 35px;
    height: 33px;
  }

  .control:hover {
    background: #fff8e8;
    color: #0e3052;
  }

  .control:active {
    box-shadow: inset 0 2px 0 #d6cbb1;
    transform: translateY(1px);
  }

  .control:focus-visible {
    outline: 2px solid #ffffff;
    outline-offset: 1px;
  }
</style>
