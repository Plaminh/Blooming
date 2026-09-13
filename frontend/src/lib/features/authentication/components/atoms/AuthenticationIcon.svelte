<script lang="ts">
  let { name, size = 24, color = 'currentColor' }: { 
    name: 'email' | 'lock' | 'checkmark' | 'minimize' | 'maximize' | 'restore' | 'close' | 'eye' | 'eye-off',
    size?: number, 
    color?: string 
  } = $props();
</script>

<svg 
  width={size} 
  height={size} 
  viewBox="0 0 24 24" 
  fill="none" 
  stroke={color} 
  stroke-width="2" 
  stroke-linecap="round" 
  stroke-linejoin="round"
  aria-hidden="true"
  focusable="false"
>
  {#if name === 'email'}
    <rect x="3" y="5" width="18" height="14" rx="2" ry="2"></rect>
    <polyline points="3 7 12 13 21 7"></polyline>
  {:else if name === 'lock'}
    <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
    <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
  {:else if name === 'checkmark'}
    <polyline points="20 6 9 17 4 12"></polyline>
  {:else if name === 'minimize'}
    <line x1="5" y1="12" x2="19" y2="12"></line>
  {:else if name === 'maximize'}
    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect>
  {:else if name === 'restore'}
    <rect x="7" y="3" width="14" height="14"></rect>
    <path d="M3 7h14v14H3z"></path>
  {:else if name === 'close'}
    <line x1="18" y1="6" x2="6" y2="18"></line>
    <line x1="6" y1="6" x2="18" y2="18"></line>
  {:else if name === 'eye'}
    <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
    <circle cx="12" cy="12" r="3"></circle>
  {:else if name === 'eye-off'}
    <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
    <line x1="1" y1="1" x2="23" y2="23"></line>
  {/if}
</svg>
