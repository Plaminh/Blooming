<script lang="ts">
  let { message, severity = 'error', dismissLabel, onDismiss }: {
    message: string;
    severity?: 'warning' | 'error' | 'success';
    dismissLabel?: string;
    onDismiss?: () => void;
  } = $props();
</script>

<div class="notification-toast {severity}" role={severity === 'error' ? 'alert' : 'status'}
  aria-live={severity === 'error' ? 'assertive' : 'polite'} data-severity={severity}>
  {#if severity === 'warning'}<span class="icon" aria-hidden="true">!</span>{/if}
  <span>{message}</span>
  {#if onDismiss}<button aria-label={dismissLabel ?? 'Dismiss'} onclick={onDismiss}>×</button>{/if}
</div>

<style>
  .notification-toast {
    position: absolute; top: 16px; left: 50%; z-index: 100;
    display: flex; max-width: min(620px, calc(100% - 32px)); align-items: center; gap: 12px;
    padding: 12px 24px; border: 1px solid transparent; border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.14); transform: translateX(-50%);
    font-family: var(--bloom-body-font);
  }
  .warning { border-color: #d39b19; background: #fff1b8; color: #684700; }
  .error { background: var(--bloom-error, #b42828); color: #fff; }
  .success { background: #d8f2df; color: #175b32; }
  .icon {
    display: grid; width: 20px; height: 20px; place-items: center; flex: 0 0 20px;
    border: 2px solid currentColor; border-radius: 50%; font-weight: 800; line-height: 1;
  }
  button { border: 0; background: transparent; color: inherit; cursor: pointer; font-size: 20px; }
</style>
