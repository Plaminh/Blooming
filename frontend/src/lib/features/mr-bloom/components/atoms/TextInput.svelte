<script lang="ts">
  let { 
    value = $bindable(''), 
    placeholder = '', 
    disabled = false,
    onkeydown
  }: { 
    value?: string;
    placeholder?: string;
    disabled?: boolean;
    onkeydown?: (e: KeyboardEvent) => void;
  } = $props();
</script>

<input 
  type="text" 
  class="bloom-text-input"
  bind:value 
  {placeholder}
  {disabled}
  {onkeydown}
/>

<style>
  .bloom-text-input {
    width: 100%;
    padding: 12px 16px;
    border: 1px solid #cfc9b9;
    border-radius: 4px;
    font-family: var(--bloom-body-font);
    font-size: 15px;
    color: #064798;
    background: #ffffff;
    box-sizing: border-box;
  }
  
  .bloom-text-input::placeholder {
    color: #92b9d4;
  }
  
  .bloom-text-input:focus {
    outline: none;
    border-color: #73c2e8;
  }
  
  .bloom-text-input:disabled {
    background: #fdfaf3;
    opacity: 0.7;
    cursor: not-allowed;
  }
</style>
