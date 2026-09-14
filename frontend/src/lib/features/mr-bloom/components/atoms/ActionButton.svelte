<script lang="ts">
  let { 
    label, 
    disabled = false, 
    variant = 'primary', 
    onclick
  }: { 
    label: string; 
    disabled?: boolean; 
    variant?: 'primary' | 'secondary' | 'ghost' | 'danger'; 
    onclick?: () => void;
  } = $props();
</script>

<button 
  class="action-button {variant}" 
  {disabled}
  {onclick}
>
  {label}
</button>

<style>
  .action-button {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border: none;
    border-radius: 4px;
    cursor: pointer;
    padding: 10px 16px;
    font-family: var(--bloom-header-font, 'Pixelify Sans', sans-serif);
    font-size: 14px;
    text-transform: uppercase;
    font-weight: 700;
    transition: all 0.2s ease;
  }
  
  .action-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
  
  .primary {
    background: #6cc164; /* Green token from references */
    color: #ffffff;
    border: 1px solid #5aa553;
  }
  
  .primary:hover:not(:disabled) {
    background: #7bd073;
  }

  .secondary {
    border: 1px solid #cfc9b9;
    background: #ffffff;
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
    background: transparent;
    color: #d14949;
  }
  
  .danger:hover:not(:disabled) {
    background: rgba(209, 73, 73, 0.1);
  }
</style>
