<script lang="ts">
  import { mrBloomStore } from '../../stores/mrBloomStore';
</script>

{#if $mrBloomStore.needsReplace}
  <div class="overlay" role="presentation" onclick={(event) => {
    if (event.target === event.currentTarget) mrBloomStore.cancelReplace();
  }}>
    <div
      class="dialog"
      role="alertdialog"
      aria-modal="true"
      aria-labelledby="replace-plan-title"
      aria-describedby="replace-plan-description"
      tabindex="-1"
    >
      <h2 id="replace-plan-title">Replace today’s plan?</h2>
      <p id="replace-plan-description">
        A saved plan already exists for this date. Confirming will replace its unfinished
        schedule with this reviewed draft. Cancel keeps both the saved plan and this draft unchanged.
      </p>
      <div class="actions">
        <button type="button" class="cancel" onclick={() => mrBloomStore.cancelReplace()} disabled={$mrBloomStore.isSavePending}>
          Cancel
        </button>
        <button type="button" class="confirm" onclick={() => mrBloomStore.confirmReplace()} disabled={$mrBloomStore.isSavePending}>
          {$mrBloomStore.isSavePending ? 'Replacing…' : 'Replace plan'}
        </button>
      </div>
    </div>
  </div>
{/if}

<style>
  .overlay { position:absolute; inset:0; z-index:1000; display:flex; align-items:center; justify-content:center; background:rgba(20,35,42,.45); }
  .dialog { width:min(420px, calc(100% - 32px)); padding:20px; border:2px solid #c9c3b5; border-radius:8px; background:#fffdf8; box-shadow:0 12px 30px rgba(0,0,0,.18); font-family:var(--bloom-body-font); }
  h2 { margin:0 0 10px; color:#06459a; font-size:20px; }
  p { margin:0; color:#31556b; line-height:1.45; }
  .actions { display:flex; justify-content:flex-end; gap:10px; margin-top:20px; }
  button { min-height:40px; padding:8px 16px; border-radius:5px; border:1px solid #71858c; font:inherit; font-weight:700; cursor:pointer; }
  button:disabled { opacity:.55; cursor:not-allowed; }
  .cancel { background:#fff; color:#31556b; }
  .confirm { border-color:#9d443c; background:#b75252; color:#fff; }
</style>
