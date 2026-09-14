<script lang="ts">
  let { disabled, onclick, text = 'UNLOCK' }: { disabled?: boolean; onclick: () => void; text?: string } = $props();
</script>

<button {disabled} {onclick} class="unlock-button" aria-disabled={disabled}>
  {text}
</button>

<style>
  .unlock-button {
    background: #5db95d;
    color: #ffffff;
    border: 4px solid #1e3a5f;
    font-family: var(--bloom-display-font);
    font-size: 24px;
    padding: 12px 48px;
    cursor: pointer;
    text-transform: uppercase;
    box-shadow: inset -4px -4px 0px 0px rgba(0, 0, 0, 0.2);
    transition: transform 0.1s;
    outline: none;
  }
  .unlock-button:focus-visible {
    outline: 2px dashed #1e3a5f;
    outline-offset: 4px;
  }
  .unlock-button:disabled {
    background: #9ba4a5;
    cursor: not-allowed;
    box-shadow: inset -4px -4px 0px 0px rgba(0, 0, 0, 0.1);
  }
  .unlock-button:active:not(:disabled) {
    box-shadow: inset 4px 4px 0px 0px rgba(0, 0, 0, 0.2);
    transform: translateY(2px);
  }
</style>
