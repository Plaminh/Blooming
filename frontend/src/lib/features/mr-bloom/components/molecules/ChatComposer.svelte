<script lang="ts">
  import TextInput from '../atoms/TextInput.svelte';
  import IconButton from '../atoms/IconButton.svelte';
  
  let { 
    value = $bindable(''), 
    placeholder = 'Choose what you want to plan first...',
    disabled = false,
    onsubmit
  }: { 
    value?: string;
    placeholder?: string;
    disabled?: boolean;
    onsubmit: (text: string) => void;
  } = $props();

  function handleSubmit() {
    if (!disabled && value.trim().length > 0) {
      onsubmit(value.trim());
      value = '';
    }
  }

  function handleKeyDown(e: KeyboardEvent) {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleSubmit();
    }
  }
</script>

<div class="chat-composer">
  <TextInput 
    bind:value 
    {placeholder} 
    {disabled} 
    onkeydown={handleKeyDown} 
  />
  <IconButton 
    icon="send" 
    label="Send" 
    variant="primary" 
    size="large"
    disabled={disabled || value.trim().length === 0}
    onclick={handleSubmit} 
  />
</div>

<style>
  .chat-composer {
    display: flex;
    gap: 10px;
    align-items: center;
    width: 100%;
    padding: 14px 15px 28px 16px;
    background: transparent;
  }
</style>
