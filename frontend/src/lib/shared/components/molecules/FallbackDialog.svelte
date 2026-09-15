<script lang="ts">
  let { title = 'Coming Soon', message = 'This feature is not yet available.', isOpen, onClose }: { title?: string; message?: string; isOpen: boolean; onClose: () => void } = $props();
</script>

{#if isOpen}
  <div class="dialog-overlay" onclick={onClose} role="presentation">
    <!-- svelte-ignore a11y_click_events_have_key_events -->
    <!-- svelte-ignore a11y_no_noninteractive_element_interactions -->
    <div class="dialog-content" tabindex="-1" onclick={(e) => e.stopPropagation()} role="dialog" aria-modal="true" aria-labelledby="dialog-title">
      <header>
        <h2 id="dialog-title">{title}</h2>
        <button class="close-btn" aria-label="Close dialog" onclick={onClose}>&times;</button>
      </header>
      <div class="dialog-body">
        <p>{message}</p>
      </div>
      <footer>
        <button class="btn-primary" onclick={onClose}>Close</button>
      </footer>
    </div>
  </div>
{/if}

<style>
  .dialog-overlay {
    position: absolute;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0, 0, 0, 0.4);
    display: flex;
    align-items: center;
    justify-content: center;
    z-index: 1000;
  }
  .dialog-content {
    background: #fffdf8;
    border: 1px solid #cfcebe;
    border-radius: 8px;
    width: 400px;
    max-width: 90vw;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
    display: flex;
    flex-direction: column;
    overflow: hidden;
  }
  header {
    background: linear-gradient(#3998ad, #24859f);
    padding: 12px 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  h2 {
    margin: 0;
    color: white;
    font-family: var(--bloom-body-font);
    font-size: 17px;
    font-weight: 700;
  }
  .close-btn {
    background: none;
    border: none;
    color: white;
    font-size: 24px;
    line-height: 1;
    cursor: pointer;
    padding: 0;
  }
  .dialog-body {
    padding: 24px 16px;
    color: #064b91;
    font-family: var(--bloom-body-font);
    font-size: 15px;
    line-height: 1.5;
  }
  p {
    margin: 0;
  }
  footer {
    padding: 12px 16px;
    display: flex;
    justify-content: flex-end;
    border-top: 1px solid #e7e2d5;
    background: #f7f6ed;
  }
  .btn-primary {
    background: linear-gradient(#4bad6a, #269553);
    border: 1px solid #1a7847;
    border-radius: 5px;
    color: white;
    font-family: var(--bloom-body-font);
    font-size: 14px;
    font-weight: 700;
    padding: 8px 20px;
    cursor: pointer;
  }
</style>
