<script lang="ts">
  import type { Snippet } from "svelte";
  import type { HTMLButtonAttributes } from "svelte/elements";
  import type { WidgetActionVariant } from "../../types/presentation";
  import PlayIcon from "../atoms/PlayIcon.svelte";
  import StopIcon from "../atoms/StopIcon.svelte";

  type Props = HTMLButtonAttributes & {
    variant?: WidgetActionVariant;
    icon?: "play" | "stop";
    label: string;
    compact?: boolean;
    children?: Snippet;
  };

  let {
    variant = "primary",
    icon,
    label,
    compact = false,
    type = "button",
    class: className = "",
    onclick,
    children,
    ...rest
  }: Props = $props();
</script>

<button
  class="widget-button {variant} {compact ? 'compact' : ''} {className}"
  {type}
  {onclick}
  {...rest}
>
  {#if icon === "play"}
    <PlayIcon />
  {:else if icon === "stop"}
    <StopIcon />
  {/if}
  <span class="label">{label}</span>
  {@render children?.()}
</button>

<style>
  .widget-button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    margin: 0;
    border-style: solid;
    border-width: var(--widget-stroke, 4px);
    border-radius: var(--widget-radius, 4px);
    font-family: var(--widget-font, inherit);
    font-size: 21px;
    font-weight: 900;
    letter-spacing: -0.025em;
    line-height: 1;
    cursor: pointer;
    white-space: nowrap;
    box-shadow: inset 0 -3px 0 rgb(14 48 82 / 18%);
  }

  .primary {
    width: var(--widget-btn-primary-w, 129px);
    height: var(--widget-btn-height, 58px);
    background: var(--widget-primary, #489d58);
    border-color: var(--widget-primary-stroke, #2a705a);
    color: var(--widget-primary-label, #cee4d1);
  }

  .secondary {
    width: var(--widget-btn-secondary-w, 149px);
    height: var(--widget-btn-height, 58px);
    background: var(--widget-cream, #faefd5);
    border-color: var(--widget-cream-stroke, #626c69);
    color: #3a5364;
  }

  .compact {
    height: var(--widget-btn-height, 58px);
    padding: 0 10px;
    font-size: 20px;
  }

  .compact.primary {
    width: var(--widget-compact-primary-w, 124px);
  }

  .compact.secondary {
    width: var(--widget-compact-secondary-w, 114px);
  }

  .widget-button :global(svg) {
    width: 21px;
    height: 21px;
    flex: 0 0 21px;
    shape-rendering: crispEdges;
  }

  .widget-button:active {
    box-shadow: inset 0 3px 0 rgb(14 48 82 / 18%);
    transform: translateY(1px);
  }

  .widget-button:focus-visible {
    outline: 2px solid #faefd5;
    outline-offset: 2px;
  }
</style>
