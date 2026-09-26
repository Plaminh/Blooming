<script lang="ts">
  import AppIcon from "$lib/shared/components/atoms/AppIcon.svelte";
  let {
    onQuickReplan,
    onAdjustWithMrBloom,
    disabled = false,
    replanDisabled = false,
    adjustDisabled = false,
  }: {
    onQuickReplan: () => void;
    onAdjustWithMrBloom: () => void;
    disabled?: boolean;
    replanDisabled?: boolean;
    adjustDisabled?: boolean;
  } = $props();
</script>

<footer class="bottom-actions">
  <button class="action quick-replan" data-testid="quick-replan-btn" onclick={onQuickReplan} disabled={disabled || replanDisabled}>
    <AppIcon name="clock" scale={0.7} />
    <span>QUICK REPLAN</span>
  </button>
  <button class="action adjust" data-testid="bottom-adjust-bloom-btn" onclick={onAdjustWithMrBloom} disabled={disabled || adjustDisabled}>
    <AppIcon name="replan" scale={0.7} />
    <span>ADJUST WITH MR. BLOOM</span>
  </button>
</footer>

<style>
  .bottom-actions {
    display: flex;
    height: 82px;
    flex: 0 0 82px;
    align-items: center;
    justify-content: flex-end;
    gap: 10px;
    padding: 12px 14px;
  }
  .action {
    display: flex;
    height: 55px;
    align-items: center;
    justify-content: center;
    gap: 9px;
    padding: 0 18px;
    border: 1px solid #aaa79f;
    border-radius: 4px;
    font-family: var(--bloom-body-font);
    font-size: 16px;
    font-weight: 700;
    white-space: nowrap;
    cursor: pointer;
  }
  .action:disabled {
    opacity: 0.55;
    cursor: not-allowed;
  }
  .quick-replan {
    width: 210px;
    background: var(--bloom-action-secondary-bg);
    color: #074a88;
  }
  .adjust {
    width: 280px;
    border-color: #177d4d;
    background: var(--bloom-action-primary-bg);
    color: #eff9ee;
  }
  .action:hover:not(:disabled) {
    filter: brightness(1.04);
  }
  .action:focus-visible {
    outline: 2px solid #00aeea;
    outline-offset: 2px;
  }
</style>
