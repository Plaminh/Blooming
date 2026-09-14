<script lang="ts">
  import { mrBloomStore } from '../../stores/mrBloomStore';
  import ChatMessage from '../molecules/ChatMessage.svelte';
  import PromptSuggestion from '../molecules/PromptSuggestion.svelte';
  import ChatComposer from '../molecules/ChatComposer.svelte';
  import LoadingDots from '../atoms/LoadingDots.svelte';
  import ChatAvatar from '../atoms/ChatAvatar.svelte';
  
  function handleSuggestion(content: string) {
    mrBloomStore.submitMessage(content);
  }
</script>

<div class="conversation-panel">
  <div class="messages-container">
    {#each $mrBloomStore.chatHistory as message (message.id)}
      <ChatMessage {message} />
    {/each}
    
    {#if $mrBloomStore.isWaitingForResponse}
      <div class="loading-container">
        <div class="avatar-container">
          <ChatAvatar />
        </div>
        <div class="bubble">
          <LoadingDots />
        </div>
      </div>
    {/if}
    
    {#if $mrBloomStore.chatHistory.length <= 1}
      <div class="suggestions">
        <PromptSuggestion 
          icon="calendar" 
          title="PLAN MY DAY" 
          description="Let's build a timeline that balances your tasks and breaks" 
          onclick={() => handleSuggestion("Plan my day. I have 6 hours.")}
        />
        <PromptSuggestion 
          icon="rocket" 
          title="PLAN A GOAL" 
          description="Break a big project into actionable milestones" 
          onclick={() => handleSuggestion("I want to complete the MVP by June 30")}
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
  
  .messages-container {
    flex: 1;
    overflow-y: auto;
    padding: 24px;
    display: flex;
    flex-direction: column;
  }
  
  .suggestions {
    margin-top: 24px;
    display: flex;
    flex-direction: column;
    gap: 12px;
  }
  
  .composer-container {
    flex-shrink: 0;
  }
  
  .loading-container {
    display: flex;
    gap: 12px;
    margin-bottom: 24px;
    width: 100%;
  }
  
  .avatar-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    width: 60px;
    flex-shrink: 0;
  }
  
  .bubble {
    background: #ffffff;
    border: 1px solid #cfc9b9;
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
    border-top: 8px solid #cfc9b9;
    border-left: 8px solid transparent;
  }
  
  .bubble::after {
    content: '';
    position: absolute;
    top: 1px;
    left: -6px;
    width: 0;
    height: 0;
    border-top: 6px solid #ffffff;
    border-left: 6px solid transparent;
  }
</style>
