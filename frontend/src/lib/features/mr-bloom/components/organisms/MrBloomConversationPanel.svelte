<script lang="ts">
  import { tick } from 'svelte';
  import { mrBloomStore } from '../../stores/mrBloomStore';
  import ChatMessage from '../molecules/ChatMessage.svelte';
  import PromptSuggestion from '../molecules/PromptSuggestion.svelte';
  import ChatComposer from '../molecules/ChatComposer.svelte';
  import LoadingDots from '../atoms/LoadingDots.svelte';
  import ChatAvatar from '../atoms/ChatAvatar.svelte';
  import PanelHeading from '../atoms/PanelHeading.svelte';
  
  let messagesContainer: HTMLDivElement | undefined = $state();

  $effect(() => {
    // Read properties to create dependencies
    const len = $mrBloomStore.chatHistory.length;
    const waiting = $mrBloomStore.isWaitingForResponse;
    
    tick().then(() => {
      if (messagesContainer) {
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
      }
    });
  });

  function handleSuggestion(content: string) {
    mrBloomStore.submitMessage(content);
  }
</script>

<div class="conversation-panel">
  <header class="panel-header">
    <PanelHeading>CHAT WITH MR. BLOOM</PanelHeading>
  </header>

  <div class="messages-container" bind:this={messagesContainer}>
    {#each $mrBloomStore.chatHistory as message (message.id)}
      <ChatMessage {message} onretry={() => mrBloomStore.retryMessage(message.id)} />
    {/each}
    
    {#if $mrBloomStore.isWaitingForResponse}
      <div class="loading-container">
        <div class="avatar-container">
          <ChatAvatar thinking />
        </div>
        <div class="bubble">
          <LoadingDots />
        </div>
      </div>
    {/if}

    {#if $mrBloomStore.error}
      <p class="chat-error" role="alert">{$mrBloomStore.error}</p>
    {/if}
    
    {#if $mrBloomStore.chatHistory.length <= 1}
      <div class="suggestions">
        <PromptSuggestion 
          icon="calendar" 
          title="PLAN MY DAY" 
          description="Turn today or tomorrow into a realistic schedule."
          selected
          onclick={() => handleSuggestion("Plan my day. I have 6 hours.")}
        />
        <PromptSuggestion 
          icon="goals"
          title="CREATE A LONG-TERM GOAL"
          description="Build a clear roadmap with milestones."
          onclick={() => handleSuggestion("I want to create a long-term goal. Help me define the outcome and target date.")}
        />
      </div>
    {/if}
  </div>
  
  <div class="composer-container">
    <ChatComposer 
      disabled={$mrBloomStore.isWaitingForResponse} 
      onsubmit={(text) => mrBloomStore.submitMessage(text)} 
    />
  </div>
</div>

<style>
  .conversation-panel {
    display: flex;
    flex-direction: column;
    height: 100%;
    width: 100%;
  }

  .panel-header {
    flex: 0 0 auto;
    padding: 12px 18px 0;
  }
  
  .messages-container {
    flex: 1;
    min-height: 0;
    overflow-y: auto;
    padding: 8px 14px 12px;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  
  .suggestions {
    margin-top: 12px;
    display: flex;
    flex-direction: column;
    gap: 9px;
  }
  
  .composer-container {
    flex-shrink: 0;
  }
  
  .loading-container {
    display: flex;
    gap: 12px;
    width: 100%;
  }
  
  .avatar-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    width: var(--bloom-chat-avatar-slot);
    flex-shrink: 0;
  }
  
  .bubble {
    background: var(--bloom-settings-panel-bg);
    border: 1px solid var(--bloom-border-light);
    padding: 12px 16px;
    border-radius: 8px;
    border-top-left-radius: 0;
    display: inline-flex;
    align-items: center;
    height: 48px;
    position: relative;
  }
  
  .bubble::before {
    content: '';
    position: absolute;
    top: 0;
    left: -8px;
    width: 0;
    height: 0;
    border-top: 8px solid var(--bloom-border-light);
    border-left: 8px solid transparent;
  }
  
  .bubble::after {
    content: '';
    position: absolute;
    top: 1px;
    left: -6px;
    width: 0;
    height: 0;
    border-top: 6px solid var(--bloom-settings-panel-bg);
    border-left: 6px solid transparent;
  }
</style>
