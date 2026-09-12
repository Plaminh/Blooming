<script lang="ts">
  import type { WidgetAction } from "../../types/presentation";
  import WidgetButton from "../atoms/WidgetButton.svelte";

  type Props = {
    actions: WidgetAction[];
  };

  let { actions }: Props = $props();

  let compact = $derived(actions.length > 2);

  function activate(action: WidgetAction) {
    action.onClick?.();
  }
</script>

{#if actions.length > 0}
  <div class="actions" class:compact>
    {#each actions as action (action.id)}
      <WidgetButton
        label={action.label}
        variant={action.variant}
        icon={action.icon}
        compact={compact}
        onclick={() => activate(action)}
      />
    {/each}
  </div>
{/if}

<style>
  .actions {
    display: flex;
    align-items: center;
    justify-content: flex-end;
    gap: var(--widget-action-gap, 9px);
  }
</style>
