<script lang="ts">
  import AppIcon from '$lib/shared/components/atoms/AppIcon.svelte';

  let { date, showIcon = true }: { date: string; showIcon?: boolean } = $props();
</script>

<div class="target-date">
  {#if showIcon}
    <AppIcon name="calendar" scale={0.7} />
  {/if}
  <span>{date}</span>
</div>

<style>
  .target-date {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    color: #0c61a1;
    font-family: var(--bloom-body-font);
    font-size: 14px;
  }
</style>
