<script lang="ts">
  let { active = false }: { active?: boolean } = $props();
</script>

<div class="timeline-marker" class:active></div>

<style>
  .timeline-marker {
    width: 12px;
    height: 12px;
    border-radius: 50%;
    background: #fdfaf3;
    border: 2px solid #cfc9b9;
    box-shadow: 0 0 0 4px #ffffff; /* create gap effect */
    z-index: 2;
    position: relative;
  }
  
  .timeline-marker.active {
    background: #a9e0f5;
    border-color: #73c2e8;
  }
</style>
