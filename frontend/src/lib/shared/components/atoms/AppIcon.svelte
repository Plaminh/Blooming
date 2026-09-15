<script lang="ts" module>
  export type IconName =
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
    | 'play'
    | 'replan'
    | 'water'
    | 'sprout'
    | 'user'
    | 'clock'
    | 'bell'
    | 'send'
    | 'edit'
    | 'close'
    | 'drag-indicator'
    | 'rocket'
    | 'chevron-right'
    | 'local_cafe'
    | 'directions_walk'
    | 'check_circle'
    | 'check'
    | 'bug';
</script>

<script lang="ts">
  let { name, scale = 1, label }: { name: IconName; scale?: number; label?: string } = $props();

  // Map known icons to real assets. Unknown icons will not render a background image until assets are provided.
  const iconAssets: Partial<Record<IconName, string>> = {
    goals: '/assets/widget/icons/leaf-icon.png',
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
  <svg
    class="app-icon fallback-svg"
    viewBox="0 0 24 24"
    role={label ? 'img' : undefined}
    aria-label={label}
    aria-hidden={!label}
    style:width="{defaultSize * scale}px"
    style:height="{defaultSize * scale}px"
    fill="currentColor"
  >
    {#if name === 'settings'}
      <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path>
      <circle cx="12" cy="12" r="3"></circle>
    {:else if name === 'user'}
      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
      <circle cx="12" cy="7" r="4"></circle>
    {:else if name === 'clock'}
      <circle cx="12" cy="12" r="10"></circle>
      <polyline points="12 6 12 12 16 14"></polyline>
    {:else if name === 'bell'}
      <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
      <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
    {:else if name === 'water'}
      <path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z" fill="#48c8f4"></path>
    {:else if name === 'today'}
      <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
      <line x1="16" y1="2" x2="16" y2="6"></line>
      <line x1="8" y1="2" x2="8" y2="6"></line>
      <line x1="3" y1="10" x2="21" y2="10"></line>
    {:else if name === 'goals'}
      <circle cx="12" cy="12" r="10"></circle>
      <circle cx="12" cy="12" r="6"></circle>
      <circle cx="12" cy="12" r="2"></circle>
    {:else if name === 'chat'}
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
      <circle cx="8" cy="10" r="1" fill="currentColor" stroke="none"></circle>
      <circle cx="12" cy="10" r="1" fill="currentColor" stroke="none"></circle>
      <circle cx="16" cy="10" r="1" fill="currentColor" stroke="none"></circle>
    {:else if name === 'calendar'}
      <path d="M4 5h16a2 2 0 0 1 2 2v14H2V7a2 2 0 0 1 2-2Z" fill="currentColor" stroke="none"></path>
      <path d="M7 3v5m10-5v5" stroke-width="2.5"></path>
      <path d="M5 10h14v2H5zm1 4h3v2H6zm5 0h3v2h-3zm5 0h2v2h-2zM6 18h3v2H6zm5 0h3v2h-3z" fill="#e6f6ff" stroke="none"></path>
    {:else if name === 'send'}
      <path d="M3 11.5 21 3l-6.7 18-3.2-7.1L3 11.5Z" fill="currentColor" stroke="none"></path>
      <path d="m11.1 13.9 4.6-5"></path>
    {:else if name === 'chevron-right'}
      <path d="m9 5 7 7-7 7" stroke-width="3"></path>
    {:else if name === 'book'}
      <path d="M3 5.5c3.2-1 6-.4 9 1.6v13c-3-2-5.8-2.6-9-1.6v-13Zm18 0c-3.2-1-6-.4-9 1.6v13c3-2 5.8-2.6 9-1.6v-13Z" fill="#e8f7ff" stroke-width="1.5"></path>
      <path d="M6 8.5c1.5-.2 2.6.1 4 .8M6 12c1.5-.2 2.6.1 4 .8m8-4.3c-1.5-.2-2.6.1-4 .8M18 12c-1.5-.2-2.6.1-4 .8"></path>
    {:else if name === 'shoe'}
      <path d="M3 14.5 9.5 7l3 3.5 2.5 1 5.5 1.2c1 .2 1.6 1.2 1.4 2.2l-.3 1.2c-.2.8-.9 1.4-1.8 1.4H7.5c-2.2 0-3.7-1-4.5-3Z" fill="#dcefff"></path>
      <path d="m8.2 9.2 2.3 2.3m-4 0L9 14m3.5-2 2.2 2"></path>
    {:else if name === 'document'}
      <path d="M5 2h11l4 4v16H5V2Z" fill="#edf9f4" stroke-width="1.8"></path>
      <path d="M16 2v5h4M8 11h9M8 15h9M8 19h6"></path>
    {:else if name === 'pencil'}
      <path d="m4 20 1.2-5.1L16.8 3.3a1.8 1.8 0 0 1 2.5 0l1.4 1.4a1.8 1.8 0 0 1 0 2.5L9.1 18.8 4 20Z"></path>
      <path d="m14.8 5.2 4 4M5.2 14.9l3.9 3.9"></path>
    {:else if name === 'play'}
      <path d="m7 4 12 8-12 8V4Z" fill="currentColor" stroke="none"></path>
    {:else}
      <rect x="2" y="2" width="20" height="20" rx="4" />
    {/if}
  </svg>
{/if}

<style>
  .app-icon {
    display: inline-block;
    flex: 0 0 auto;
    image-rendering: pixelated;
  }
  .fallback-svg {
    fill: none;
    stroke: currentColor;
    stroke-width: 2;
    stroke-linecap: round;
    stroke-linejoin: round;
  }
</style>
