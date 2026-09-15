<script lang="ts">
  import MrBloomCharacter from '$lib/features/companion-widget/components/atoms/MrBloomCharacter.svelte';
</script>

<div class="chat-avatar">
  <div class="character-crop">
    <div class="character-position">
      <MrBloomCharacter kind="reminders" />
    </div>
  </div>
  <img class="avatar-leaf" src="/assets/widget/icons/leaf-icon.png" alt="" />
</div>

<style>
  .chat-avatar {
    position: relative;
    width: 140px;
    height: 112px;
  }

  .character-crop {
    position: absolute;
    inset: 10px 0 0;
    overflow: hidden;
  }

  .character-position {
    position: absolute;
    left: -23px;
    top: 0;
  }

  .avatar-leaf {
    position: absolute;
    z-index: 1;
    top: -7px;
    left: 54px;
    width: 46px;
    height: 46px;
    object-fit: contain;
    image-rendering: pixelated;
  }
</style>
