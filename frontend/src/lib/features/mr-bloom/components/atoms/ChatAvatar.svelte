<script lang="ts">
  import MrBloomCharacter from '$lib/features/companion-widget/components/atoms/MrBloomCharacter.svelte';
  let { thinking = false }: { thinking?: boolean } = $props();
</script>

<div class="chat-avatar">
  <div class="character-position">
    <MrBloomCharacter animation={thinking ? 'thinking' : 'idle'} displayHeight={60} />
  </div>
</div>

<style>
  .chat-avatar {
    position: relative;
    width: var(--bloom-chat-avatar-width);
    height: var(--bloom-chat-avatar-height);
  }

  .character-position {
    position: absolute;
    left: -13px;
    top: 4px;
  }
</style>
