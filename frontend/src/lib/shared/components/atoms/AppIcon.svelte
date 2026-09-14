<script lang="ts">
  type IconName =
    | 'today'
    | 'goals'
    | 'chat'
    | 'settings'
    | 'book'
    | 'break'
    | 'document'
    | 'shoe'
    | 'calendar'
    | 'event'
    | 'category'
    | 'notes'
    | 'pencil'
    | 'replan'
    | 'water'
    | 'sprout';

  let { name, scale = 1, label }: { name: IconName; scale?: number; label?: string } = $props();

  // Map known icons to real assets. Unknown icons will not render a background image until assets are provided.
  const iconAssets: Partial<Record<IconName, string>> = {
    sprout: '/assets/widget/icons/leaf-icon.png'
  };

  const src = $derived(iconAssets[name]);
  
  // Base size fallback if no intrinsic size from image
  const defaultSize = 24;
</script>

{#if src}
  <img 
    class="app-icon" 
    {src} 
    alt={label || ""} 
    aria-hidden={!label} 
    style:width="{defaultSize * scale}px" 
    style:height="auto" 
  />
{:else}
  <span 
    class="app-icon placeholder" 
    role={label ? 'img' : undefined} 
    aria-label={label}
    style:width="{defaultSize * scale}px"
    style:height="{defaultSize * scale}px"
  ></span>
{/if}

<style>
  .app-icon {
    display: inline-block;
    flex: 0 0 auto;
    image-rendering: pixelated;
  }
  .placeholder {
    /* Transparent placeholder for missing assets */
    display: inline-block;
  }
</style>
