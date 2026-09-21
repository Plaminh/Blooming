<script lang="ts">
  let { label, variant, disabled = false, onclick }: { label: string; variant: 'task' | 'milestone'; disabled?: boolean; onclick?: () => void } = $props();
</script>

<button class="add-draft-btn variant-{variant}" {disabled} {onclick}>
  <span aria-hidden="true">+</span>
  {label}
</button>

<style>
  .add-draft-btn {
    display: flex;
    align-items: center;
    border: 2px solid var(--bloom-border-draft);
    border-radius: 5px;
    background: var(--bloom-action-secondary-bg);
    color: var(--bloom-text-draft);
    font-family: var(--bloom-display-font);
    font-weight: 800;
    letter-spacing: -0.055em;
    cursor: pointer;
  }

  .add-draft-btn.variant-task {
    width: 184px;
    height: 48px;
    flex: 0 0 48px;
    gap: 12px;
    padding: 0 18px;
    font-size: 18px;
  }
  .add-draft-btn.variant-task span {
    font-size: var(--bloom-icon-control);
  }

  .add-draft-btn.variant-milestone {
    width: 226px;
    height: 46px;
    flex: 0 0 46px;
    gap: 12px;
    margin-top: 1px;
    padding: 0 22px;
    font-size: 18px;
  }
  .add-draft-btn.variant-milestone span {
    font-size: 31px;
  }

  .add-draft-btn span {
    font-family: var(--bloom-body-font);
    line-height: 1;
    font-weight: 300;
  }

  .add-draft-btn:hover:not(:disabled) { background: var(--bloom-action-draft-hover); }
  .add-draft-btn:focus-visible:not(:disabled) { outline: 2px solid var(--bloom-action-draft-focus); outline-offset: 2px; }
  .add-draft-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
</style>
