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
    height: 72px;
    padding: 0 14px;
    border: 2px solid #c9c3b5;
    border-radius: 7px;
    font-family: var(--bloom-body-font);
    font-size: 19px;
    color: #064798;
    background: rgba(255, 255, 255, 0.7);
    box-sizing: border-box;
  }
  
  .bloom-text-input::placeholder {
    color: #6aa2c6;
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
