<script lang="ts">
</script>

<div class="chat-avatar">
  <div class="sprite-wrapper">
    <!-- Fallback avatar image to fix type errors -->
    <img src="/assets/widget/icons/leaf-icon.png" alt="Mr. Bloom" width="48" height="48" style="image-rendering: pixelated;" />
  </div>
</div>

<style>
  .chat-avatar {
    width: 48px;
    height: 48px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: transparent;
  }
  
  .sprite-wrapper {
    transform: scale(1.5);
  }
</style>
