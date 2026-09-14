<script lang="ts">
  import type { ChatMessage as ChatMessageType } from '../../stores/mrBloomStore';
  import ChatAvatar from '../atoms/ChatAvatar.svelte';
  
  let { message }: { message: ChatMessageType } = $props();
</script>

<div class="chat-message {message.role}">
  {#if message.role === 'assistant'}
    <div class="avatar-container">
      <ChatAvatar />
      <span class="name">Mr. Bloom</span>
      <span class="time">{message.timestamp}</span>
    </div>
  {/if}
  
  <div class="bubble">
    {message.content}
    {#if message.role === 'user'}
      <span class="time user-time">{message.timestamp}</span>
    {/if}
  </div>
</div>

<style>
  .chat-message {
    display: flex;
    gap: 12px;
    margin-bottom: 24px;
    width: 100%;
  }
  
  .chat-message.user {
    justify-content: flex-end;
  }
  
  .avatar-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 4px;
    width: 60px;
    flex-shrink: 0;
  }
  
  .name {
    font-family: var(--bloom-body-font);
    font-weight: 700;
    color: #064798;
    font-size: 12px;
    text-align: center;
  }
  
  .time {
    font-family: var(--bloom-body-font);
    color: #92b9d4;
    font-size: 11px;
  }
  
  .bubble {
    background: #ffffff;
    border: 1px solid #cfc9b9;
    padding: 12px 16px;
    border-radius: 8px;
    font-family: var(--bloom-body-font);
    font-size: 15px;
    color: #064798;
    line-height: 1.4;
    position: relative;
    max-width: 80%;
  }
  
  .assistant .bubble {
    border-top-left-radius: 0;
  }
  
  .assistant .bubble::before {
    content: '';
    position: absolute;
    top: 0;
    left: -8px;
    width: 0;
    height: 0;
    border-top: 8px solid #cfc9b9;
    border-left: 8px solid transparent;
  }
  
  .assistant .bubble::after {
    content: '';
    position: absolute;
    top: 1px;
    left: -6px;
    width: 0;
    height: 0;
    border-top: 6px solid #ffffff;
    border-left: 6px solid transparent;
  }
  
  .user .bubble {
    background: #e1f5ff;
    border-color: #a9e0f5;
    border-bottom-right-radius: 0;
    position: relative;
    padding-bottom: 24px; /* Space for time */
  }
  
  .user .bubble::before {
    content: '';
    position: absolute;
    bottom: -1px;
    right: -8px;
    width: 0;
    height: 0;
    border-bottom: 8px solid #a9e0f5;
    border-right: 8px solid transparent;
  }
  
  .user .bubble::after {
    content: '';
    position: absolute;
    bottom: 0px;
    right: -6px;
    width: 0;
    height: 0;
    border-bottom: 6px solid #e1f5ff;
    border-right: 6px solid transparent;
  }
  
  .user-time {
    position: absolute;
    bottom: 8px;
    right: 12px;
  }
</style>
