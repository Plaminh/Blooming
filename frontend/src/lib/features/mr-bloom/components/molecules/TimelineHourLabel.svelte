<script lang="ts">
  let { hour }: { hour: string } = $props();
</script>

<div class="timeline-hour-label">
  {hour}
</div>

<style>
  .timeline-hour-label {
    font-family: var(--bloom-body-font);
    font-size: 13px;
    font-weight: 700;
    color: #92b9d4;
    width: 48px;
    text-align: right;
  }
</style>
