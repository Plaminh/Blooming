<script lang="ts">
  let { 
    type, 
    title, 
    subtitle 
  }: { 
    type: string; 
    title: string; 
    subtitle?: string; 
  } = $props();
</script>

<div class="draft-review-header">
  <div class="type-label">LIVE DRAFT • {type}</div>
  <h2 class="title">{title}</h2>
  {#if subtitle}
    <p class="subtitle">{subtitle}</p>
  {/if}
</div>

<style>
  .draft-review-header {
    padding: 24px;
    border-bottom: 1px solid #cfc9b9;
    flex-shrink: 0;
  }
  
  .type-label {
    font-family: var(--bloom-body-font);
    font-size: 11px;
    font-weight: 700;
    color: #92b9d4;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 8px;
  }
  
  .title {
    font-family: var(--bloom-header-font, 'Pixelify Sans', sans-serif);
    font-size: 24px;
    color: #064798;
    margin: 0;
    text-transform: uppercase;
  }
  
  .subtitle {
    font-family: var(--bloom-body-font);
    font-size: 15px;
    color: #064798;
    margin: 8px 0 0 0;
  }
</style>
