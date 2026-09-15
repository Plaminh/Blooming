<script lang="ts">
  import AppIcon from '$lib/shared/components/atoms/AppIcon.svelte';
  import { getSettingsState } from '../../model/SettingsState.svelte';

  const settingsState = getSettingsState();
</script>

<section class="panel account-panel" aria-labelledby="account-heading">
  <div class="panel-header">
    <AppIcon name="user" scale={1.2} />
    <h3 id="account-heading">ACCOUNT</h3>
  </div>
  
  <div class="account-content">
    <div class="account-info">
      <span class="account-label">Signed in as</span>
      <span class="account-email">{settingsState.draftSettings.email}</span>
    </div>
    
    <button class="btn-logout" type="button" onclick={() => settingsState.logout()}>
      LOGOUT
    </button>
  </div>
</section>

<style>
  .panel {
    background: var(--bloom-surface-cream-alt);
    border: 1px solid var(--bloom-border-subtle);
    border-radius: 8px;
    padding: 18px;
    margin-bottom: 16px;
  }

  .panel-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 16px;
  }

  h3 {
    font-family: var(--bloom-display-font);
    font-size: 18px;
    color: var(--bloom-text-dark-blue);
    margin: 0;
  }

  .account-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }

  .account-info {
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .account-label {
    font-family: var(--bloom-body-font);
    font-size: 14px;
    color: #666;
  }

  .account-email {
    font-family: var(--bloom-body-font);
    font-size: 18px;
    font-weight: 600;
    color: var(--bloom-text-dark-blue);
  }

  .btn-logout {
    font-family: var(--bloom-display-font);
    font-size: 14px;
    padding: 8px 16px;
    border: 1px solid var(--bloom-error);
    background: transparent;
    color: var(--bloom-error);
    border-radius: 4px;
    cursor: pointer;
    text-transform: uppercase;
  }

  .btn-logout:focus-visible {
    outline: 2px solid var(--bloom-error);
    outline-offset: 2px;
  }
</style>
