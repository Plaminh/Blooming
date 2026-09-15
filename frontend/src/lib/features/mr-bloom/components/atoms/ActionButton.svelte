<script lang="ts">
  import AppIcon, { type IconSize } from '$lib/shared/components/atoms/AppIcon.svelte';

  let { 
    label, 
    disabled = false, 
    variant = 'primary', 
    icon,
    iconSize,
    onclick
  }: { 
    label: string; 
    disabled?: boolean; 
    variant?: 'primary' | 'secondary' | 'ghost' | 'danger'; 
    icon?: 'play';
    iconSize?: IconSize;
    onclick?: () => void;
  } = $props();
</script>

<button 
  class="action-button {variant}" 
  {disabled}
  {onclick}
>
  {#if icon}<AppIcon name={icon} size={iconSize} scale={1.25} />{/if}
  <span>{label}</span>
</button>

<style>
  .action-button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 58px;
    gap: 10px;
    border: 2px solid #9e9a8f;
    border-radius: 5px;
    cursor: pointer;
    padding: 8px 12px;
    font-family: var(--bloom-display-font);
    font-size: 19px;
    text-transform: uppercase;
    font-weight: var(--bloom-action-weight);
    letter-spacing: var(--bloom-action-tracking);
    transition: background 0.15s ease;
  }
  
  .action-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  .primary {
    background: var(--bloom-action-primary-bg);
    color: #ffffff;
    border-color: #227846;
  }
  
  .primary:hover:not(:disabled) {
    background: #7bd073;
  }

  .secondary {
    background: #fffaf0;
    color: #064798;
  }
  
  .secondary:hover:not(:disabled) {
    background: #fdfaf3;
  }
  
  .ghost {
    background: transparent;
    color: #064798;
  }
  
  .ghost:hover:not(:disabled) {
    background: rgba(0,0,0,0.05);
  }
  
  .danger {
    background: #fffaf0;
    color: #064798;
  }
  
  .danger:hover:not(:disabled) {
    border-color: #b75252;
    background: #fff0eb;
    color: #b13939;
  }

  .action-button:focus-visible {
    outline: 2px solid #00aeea;
    outline-offset: 2px;
  }
</style>
