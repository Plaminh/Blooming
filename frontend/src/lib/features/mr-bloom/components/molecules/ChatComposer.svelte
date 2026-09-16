<script lang="ts">
  import TextInput from '$lib/shared/components/atoms/TextInput.svelte';
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
    variant="composer"
  />
  <IconButton 
    icon="send" 
    label="Send" 
    variant="primary" 
    size="large"
    iconSize="detail"
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
    padding: 10px 14px 18px;
    background: transparent;
  }
</style>
