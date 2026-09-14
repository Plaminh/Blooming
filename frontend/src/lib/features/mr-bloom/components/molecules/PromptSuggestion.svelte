<script lang="ts">
  import AppIcon, { type IconName } from '$lib/shared/components/atoms/AppIcon.svelte';

  let { 
    icon, 
    title, 
    description,
    onclick
  }: { 
    icon: IconName; 
    title: string; 
    description: string;
    onclick: () => void;
  } = $props();
</script>

<button class="prompt-suggestion" {onclick}>
  <div class="icon-container">
    <AppIcon name={icon} scale={1.5} />
  </div>
  <div class="content">
    <div class="title">{title}</div>
    <div class="description">{description}</div>
  </div>
  <div class="arrow">
    <AppIcon name="chevron-right" />
  </div>
</button>

<style>
  .prompt-suggestion {
    display: flex;
    align-items: center;
    width: 100%;
    background: #e1f5ff;
    border: 1px solid #a9e0f5;
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 12px;
    cursor: pointer;
    text-align: left;
    transition: all 0.2s ease;
  }
  
  .prompt-suggestion:hover {
    background: #d0f0ff;
  }
  
  .icon-container {
    width: 48px;
    display: flex;
    justify-content: center;
    margin-right: 16px;
  }
  
  .content {
    flex: 1;
  }
  
  .title {
    font-family: var(--bloom-header-font, 'Pixelify Sans', sans-serif);
    font-size: 18px;
    font-weight: 700;
    color: #064798;
    margin-bottom: 4px;
    text-transform: uppercase;
  }
  
  .description {
    font-family: var(--bloom-body-font);
    font-size: 14px;
    color: #064798;
  }
  
  .arrow {
    color: #064798;
    opacity: 0.5;
  }
</style>
