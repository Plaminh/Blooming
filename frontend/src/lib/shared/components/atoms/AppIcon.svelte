<script lang="ts" module>
  export type IconSize = 'navigation' | 'task-type' | 'detail' | 'roadmap-milestone' | 'goal-list' | 'goal-detail' | 'control' | 'garden-balance' | 'garden-cost' | 'counter-water';

  export const ICON_NAMES = [
    'today',
    'goals',
    'chat',
    'settings',
    'book',
    'break',
    'document',
    'shoe',
    'calendar',
    'event',
    'category',
    'notes',
    'pencil',
    'play',
    'replan',
    'water',
    'sprout',
    'user',
    'clock',
    'bell',
    'send',
    'edit',
    'close',
    'drag-indicator',
    'rocket',
    'chevron-right',
    'local_cafe',
    'directions_walk',
    'check_circle',
    'check',
    'bug',
    'statistics'
  ] as const;

  export type IconName = typeof ICON_NAMES[number];
</script>

<script lang="ts">
  let { name, size, scale = 1, label }: {
    name: IconName;
    size?: IconSize;
    scale?: number;
    label?: string;
  } = $props();

  // Semantic sizes take precedence; legacy scales keep other assets unchanged.
  const iconSizes: Record<IconSize, string> = {
    navigation: 'var(--bloom-icon-navigation)',
    'task-type': 'var(--bloom-icon-task-type)',
    detail: 'var(--bloom-icon-detail)',
    'roadmap-milestone': 'var(--bloom-icon-roadmap-milestone)',
    'goal-list': 'var(--bloom-icon-goal-list)',
    'goal-detail': 'var(--bloom-icon-goal-detail)',
    control: 'var(--bloom-icon-control)',
    'garden-balance': 'var(--bloom-icon-garden-balance)',
    'garden-cost': 'var(--bloom-icon-garden-cost)',
    'counter-water': 'var(--bloom-icon-counter-water)'
  };

  // Map known icons to real assets. Unknown icons will not render a background image until assets are provided.
  const iconAssets: Partial<Record<IconName, string>> = {
    sprout: '/assets/icons/leaf-icon.png',
    water: '/assets/icons/water-icon.png'
  };

  const src = $derived(iconAssets[name]);
  
  // Base size fallback if no intrinsic size from image
  const defaultSize = 24;
  const renderedSize = $derived(size ? iconSizes[size] : `${defaultSize * scale}px`);
</script>

{#if src}
  <img 
    class="app-icon" 
    data-icon={name}
    data-icon-size={size}
    {src} 
    alt={label || ""} 
    aria-hidden={!label} 
    style:width={renderedSize}
    style:height="auto" 
  />
{:else}
  <svg
    class="app-icon fallback-svg"
    data-icon={name}
    data-icon-size={size}
    viewBox="0 0 24 24"
    role={label ? 'img' : undefined}
    aria-label={label}
    aria-hidden={!label}
    style:width={renderedSize}
    style:height={renderedSize}
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
    {:else if name === 'today' || name === 'calendar' || name === 'event'}
      <rect x="3" y="5" width="18" height="16" rx="2"></rect>
      <path d="M8 3v4m8-4v4M3 10h18"></path>
      <path d="M7 14h1m3 0h1m3 0h1M7 17h1m3 0h1m3 0h1"></path>
    {:else if name === 'goals'}
      <path d="M6 21V3" stroke="currentColor"></path>
      <path d="M6 4h12l-2.7 4L18 12H6Z" stroke="currentColor"></path>
      <path d="M3.5 21h5" stroke="currentColor"></path>
    {:else if name === 'chat'}
      <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
      <circle cx="8" cy="10" r="1" fill="currentColor" stroke="none"></circle>
      <circle cx="12" cy="10" r="1" fill="currentColor" stroke="none"></circle>
      <circle cx="16" cy="10" r="1" fill="currentColor" stroke="none"></circle>
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
    {:else if name === 'break'}
      <path d="M6 2v8m-3-8v5c0 2 1 3 3 3s3-1 3-3V2M6 10v12M16 2v20M16 2c3 2 4 5 4 9h-4" stroke-width="2.2"></path>
    {:else if name === 'pencil'}
      <path d="m4 20 1.2-5.1L16.8 3.3a1.8 1.8 0 0 1 2.5 0l1.4 1.4a1.8 1.8 0 0 1 0 2.5L9.1 18.8 4 20Z"></path>
      <path d="m14.8 5.2 4 4M5.2 14.9l3.9 3.9"></path>
    {:else if name === 'close'}
      <path d="M5 5 19 19M19 5 5 19" stroke-width="2.4"></path>
    {:else if name === 'play'}
      <path d="m7 4 12 8-12 8V4Z" fill="currentColor" stroke="none"></path>
    {:else if name === 'statistics'}
      <path d="M4 20v-6h4v6H4zm6 0v-10h4v10h-4zm6 0V6h4v14h-4z" fill="currentColor" stroke="none"></path>
    {:else if name === 'category'}
      <path d="M4 4h6v6H4zm10 0h6v6h-6zM4 14h6v6H4zm10 3a3 3 0 1 0 6 0 3 3 0 1 0-6 0"></path>
    {:else if name === 'notes'}
      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
      <polyline points="14 2 14 8 20 8"></polyline>
      <line x1="16" y1="13" x2="8" y2="13"></line>
      <line x1="16" y1="17" x2="8" y2="17"></line>
      <polyline points="10 9 9 9 8 9"></polyline>
    {:else if name === 'replan'}
      <polyline points="1 4 1 10 7 10"></polyline>
      <polyline points="23 20 23 14 17 14"></polyline>
      <path d="M20.49 9A9 9 0 0 0 5.64 5.64L1 10m22 4l-4.64 4.36A9 9 0 0 1 3.51 15"></path>
    {:else if name === 'edit'}
      <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
      <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
    {:else if name === 'drag-indicator'}
      <circle cx="9" cy="5" r="1"></circle>
      <circle cx="9" cy="12" r="1"></circle>
      <circle cx="9" cy="19" r="1"></circle>
      <circle cx="15" cy="5" r="1"></circle>
      <circle cx="15" cy="12" r="1"></circle>
      <circle cx="15" cy="19" r="1"></circle>
    {:else if name === 'rocket'}
      <path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"></path>
      <path d="m12 15-3-3a22 22 0 0 1-2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"></path>
      <path d="M9 12H4s.55-3.03 2-4c1.62-1.08 5 0 5 0"></path>
      <path d="M12 15v5s3.03-.55 4-2c1.08-1.62 0-5 0-5"></path>
    {:else if name === 'local_cafe'}
      <path d="M18 8h1a4 4 0 0 1 0 8h-1"></path>
      <path d="M2 8h16v9a4 4 0 0 1-4 4H6a4 4 0 0 1-4-4V8z"></path>
      <line x1="6" y1="1" x2="6" y2="4"></line>
      <line x1="10" y1="1" x2="10" y2="4"></line>
      <line x1="14" y1="1" x2="14" y2="4"></line>
    {:else if name === 'directions_walk'}
      <circle cx="12" cy="5" r="2"></circle>
      <path d="M13 22l-2-6-2 6-2-6 2-10 6 3 2-2"></path>
      <path d="M12 8l-4 4 1 2 4-2 3 5 4-3"></path>
    {:else if name === 'check_circle'}
      <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
      <polyline points="22 4 12 14.01 9 11.01"></polyline>
    {:else if name === 'check'}
      <polyline points="20 6 9 17 4 12"></polyline>
    {:else if name === 'bug'}
      <rect x="8" y="6" width="8" height="14" rx="4"></rect>
      <path d="M12 2v4"></path>
      <path d="m19 7-3 2"></path>
      <path d="m5 7 3 2"></path>
      <path d="m19 19-3-2"></path>
      <path d="m5 19 3-2"></path>
      <path d="M20 13h-4"></path>
      <path d="M4 13h4"></path>
    {:else}
      <path d="M0 0 L24 24 M24 0 L0 24" stroke="currentColor" data-error="true"></path>
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
