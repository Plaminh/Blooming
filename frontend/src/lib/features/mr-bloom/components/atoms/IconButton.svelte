<script lang="ts">
  import AppIcon, { type IconName } from '$lib/shared/components/atoms/AppIcon.svelte';

  let { 
    icon, 
    label, 
    disabled = false, 
    variant = 'primary', 
    size = 'medium',
    onclick
  }: { 
    icon: IconName; 
    label: string; 
    disabled?: boolean; 
    variant?: 'primary' | 'secondary' | 'ghost'; 
    size?: 'small' | 'medium' | 'large';
    onclick?: () => void;
  } = $props();
</script>

<button 
  class="icon-button {variant} {size}" 
  aria-label={label}
  {disabled}
  {onclick}
>
  <AppIcon name={icon} />
</button>

<style>
  .icon-button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border: none;
    border-radius: 7px;
    cursor: pointer;
    background: transparent;
    padding: 8px;
    transition: all 0.2s ease;
  }
  
  .icon-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  .primary {
    background: #e0f5ff;
    border: 2px solid #83c4ed;
    color: #6189a0;
  }
  
  .primary:hover:not(:disabled) {
    background: #8bd2f0;
  }

  .secondary {
    border: 1px solid #cfc9b9;
    background: #ffffff;
  }
  
  .secondary:hover:not(:disabled) {
    background: #fdfaf3;
  }
  
  .ghost {
    background: transparent;
  }
  
  .ghost:hover:not(:disabled) {
    background: rgba(0,0,0,0.05);
  }

  .small { padding: 4px; }
  .medium { padding: 8px; }
  .large {
    width: 72px;
    height: 72px;
    padding: 15px;
  }

  .large :global(.app-icon) {
    width: 42px !important;
    height: 42px !important;
  }
</style>
