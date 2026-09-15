<script lang="ts">
  import AppIcon from '$lib/shared/components/atoms/AppIcon.svelte';

  let { 
    label, 
    disabled = false, 
    variant = 'primary', 
    icon,
    onclick
  }: { 
    label: string; 
    disabled?: boolean; 
    variant?: 'primary' | 'secondary' | 'ghost' | 'danger'; 
    icon?: 'play';
    onclick?: () => void;
  } = $props();
</script>

<button 
  class="action-button {variant}" 
  {disabled}
  {onclick}
>
  {#if icon}<AppIcon name={icon} scale={1.25} />{/if}
  <span>{label}</span>
</button>

<style>
  .action-button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    width: 100%;
    height: 70px;
    gap: 14px;
    border: 2px solid #9e9a8f;
    border-radius: 5px;
    cursor: pointer;
    padding: 10px 16px;
    font-family: var(--bloom-display-font);
    font-size: 23px;
    text-transform: uppercase;
    font-weight: 700;
    letter-spacing: -0.055em;
    transition: background 0.15s ease;
  }
  
  .action-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  .primary {
    background: linear-gradient(180deg, #58ad68 0%, #3e9755 100%);
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
