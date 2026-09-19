<script lang="ts">
  import AppIcon, { type IconName, type IconSize } from '$lib/shared/components/atoms/AppIcon.svelte';

  let { 
    icon, 
    label, 
    disabled = false, 
    variant = 'primary', 
    size = 'medium',
    iconSize,
    onclick
  }: { 
    icon: IconName; 
    label: string; 
    disabled?: boolean; 
    variant?: 'primary' | 'secondary' | 'ghost'; 
    size?: 'small' | 'medium' | 'large';
    iconSize?: IconSize;
    onclick?: () => void;
  } = $props();
</script>

<button 
  class="icon-button {variant} {size}" 
  aria-label={label}
  {disabled}
  {onclick}
>
  <AppIcon name={icon} size={iconSize} scale={size === 'large' ? 1.75 : 1} />
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
    background: var(--bloom-chat-msg-user-bg);
    border: 2px solid var(--bloom-chat-msg-user-border);
    color: #a64e76;
  }
  
  .primary:hover:not(:disabled) {
    background: #ffd0e1;
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

</style>
