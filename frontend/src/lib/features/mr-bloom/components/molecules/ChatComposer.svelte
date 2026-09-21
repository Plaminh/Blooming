<script lang="ts">
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
    if (e.isComposing || e.keyCode === 229) return;
    
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  }
</script>

<div class="chat-composer">
  <textarea 
    bind:value 
    {placeholder} 
    {disabled} 
    onkeydown={handleKeyDown} 
    class="composer-textarea"
    rows="1"
  ></textarea>
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
  
  .composer-textarea {
    flex: 1;
    height: 72px;
    padding: 14px;
    border: 2px solid var(--bloom-chat-border);
    border-radius: 7px;
    font-size: 19px;
    background: var(--bloom-chat-surface);
    font-family: var(--bloom-body-font);
    color: var(--bloom-text-dark-blue);
    resize: none;
    box-sizing: border-box;
  }

  .composer-textarea::placeholder {
    color: var(--bloom-text-muted-blue);
  }

  .composer-textarea:focus {
    outline: none;
    border-color: var(--bloom-chat-border-focus);
  }

  .composer-textarea:disabled {
    background: var(--bloom-chat-surface-disabled);
    opacity: 0.7;
    cursor: not-allowed;
  }
</style>
