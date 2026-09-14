<script lang="ts">
  import TodayIcon from '../atoms/TodayIcon.svelte';
  let { timeText, durationText }: { timeText: string; durationText: string } = $props();
</script>

<div class="next-session-content">
  <TodayIcon name="event" scale={0.75} />
  <div>
    <p>{timeText}</p>
    <span>{durationText}</span>
  </div>
</div>

<style>
  .next-session-content {
    display: flex;
    align-items: center;
    gap: 15px;
    padding: 3px 14px 7px 43px;
    color: #0751a1;
    font-family: var(--bloom-body-font);
  }
  p { margin: 0; font-size: 16px; line-height: 1.3; }
  span { font-size: 14px; line-height: 1.2; }
</style>
