<script lang="ts">
  let { class: className = '' }: { class?: string } = $props();
</script>

<svg class="lock-icon {className}" width="20" height="24" viewBox="0 0 10 12" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true" style="image-rendering: pixelated;">
  <!-- Pixel art lock -->
  <!-- Shackle -->
  <rect x="3" y="0" width="4" height="1" fill="#1e3a5f" />
  <rect x="2" y="1" width="1" height="4" fill="#1e3a5f" />
  <rect x="7" y="1" width="1" height="4" fill="#1e3a5f" />
  <rect x="3" y="1" width="4" height="4" fill="#fbfaf5" />
  
  <!-- Body Outline -->
  <rect x="1" y="5" width="8" height="1" fill="#1e3a5f" />
  <rect x="0" y="6" width="1" height="5" fill="#1e3a5f" />
  <rect x="9" y="6" width="1" height="5" fill="#1e3a5f" />
  <rect x="1" y="11" width="8" height="1" fill="#1e3a5f" />
  
  <!-- Body Fill -->
  <rect x="1" y="6" width="8" height="5" fill="#f5eddc" />
  <rect x="1" y="6" width="1" height="5" fill="#29b9ce" />
  <rect x="8" y="6" width="1" height="5" fill="#29b9ce" />
  
  <!-- Keyhole -->
  <rect x="4" y="7" width="2" height="2" fill="#1e3a5f" />
  <rect x="4" y="9" width="2" height="1" fill="#1e3a5f" />
</svg>

<style>
  .lock-icon {
    display: inline-block;
  }
</style>
