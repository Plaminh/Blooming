<script lang="ts">
  let { direction, class: className = '' }: { direction: 'previous' | 'next'; class?: string } = $props();
</script>

<svg 
  class="carousel-arrow {className}" 
  width="44" 
  height="44" 
  viewBox="0 0 22 22" 
  fill="none" 
  xmlns="http://www.w3.org/2000/svg" 
  style="transform: scaleX({direction === 'previous' ? 1 : -1}); image-rendering: pixelated;"
  aria-hidden="true"
>
  <!-- Background / Button Body -->
  <rect x="1" y="1" width="20" height="20" fill="#f5eddc" />
  
  <!-- Borders -->
  <rect x="1" y="0" width="20" height="1" fill="#1e3a5f" />
  <rect x="1" y="21" width="20" height="1" fill="#1e3a5f" />
  <rect x="0" y="1" width="1" height="20" fill="#1e3a5f" />
  <rect x="21" y="1" width="1" height="20" fill="#1e3a5f" />
  
  <!-- Inner Highlight/Shadow -->
  <rect x="1" y="1" width="20" height="1" fill="#ffffff" />
  <rect x="1" y="20" width="20" height="1" fill="#cbc6b9" />
  
  <!-- Arrow Graphic (Pointing Left) -->
  <rect x="10" y="7" width="2" height="2" fill="#1e3a5f" />
  <rect x="8" y="9" width="2" height="2" fill="#1e3a5f" />
  <rect x="6" y="11" width="2" height="2" fill="#1e3a5f" />
  <rect x="8" y="13" width="2" height="2" fill="#1e3a5f" />
  <rect x="10" y="15" width="2" height="2" fill="#1e3a5f" />
</svg>

<style>
  .carousel-arrow {
    display: block;
  }
</style>
