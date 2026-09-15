<script lang="ts">
  import AppIcon from '$lib/shared/components/atoms/AppIcon.svelte';
  let { timeText, durationText }: { timeText: string; durationText: string } = $props();
</script>

<div class="next-session-content">
  <AppIcon name="event" scale={0.75} />
  <div>
    <p>{timeText}</p>
    <span>{durationText}</span>
  </div>
</div>

<style>
  .next-session-content {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 1px 10px 5px 34px;
    color: #0751a1;
    font-family: var(--bloom-body-font);
  }
  p { margin: 0; font-size: 14px; line-height: 1.25; }
  span { font-size: 12px; line-height: 1.15; }
</style>
