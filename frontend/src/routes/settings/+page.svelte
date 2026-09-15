<script lang="ts">
  import DesktopAppShell from '$lib/shared/components/organisms/DesktopAppShell.svelte';
  import SectionHeading from '$lib/features/settings/components/atoms/SectionHeading.svelte';
  import AccountPanel from '$lib/features/settings/components/organisms/AccountPanel.svelte';
  import GeneralPanel from '$lib/features/settings/components/organisms/GeneralPanel.svelte';
  import FocusTimerPanel from '$lib/features/settings/components/organisms/FocusTimerPanel.svelte';
  import NotificationsPanel from '$lib/features/settings/components/organisms/NotificationsPanel.svelte';
  import SettingsActionGroup from '$lib/features/settings/components/molecules/SettingsActionGroup.svelte';
  import { setSettingsState } from '$lib/features/settings/model/SettingsState.svelte';

  // Initialize form state
  setSettingsState();
</script>

<svelte:head>
  <title>Settings - Blooming</title>
</svelte:head>

<DesktopAppShell activeRoute="SETTINGS" variant="standard">
  <main class="settings-main" aria-label="Settings content">
    <div class="settings-scroll-container">
      <div class="settings-inner">
        <SectionHeading title="SETTINGS" />

        <AccountPanel />

        <div class="settings-grid">
          <div class="grid-column">
            <GeneralPanel />
          </div>

          <div class="grid-column">
            <FocusTimerPanel />
            <NotificationsPanel />
          </div>
        </div>

        <SettingsActionGroup />
      </div>
    </div>
  </main>
</DesktopAppShell>

<style>
  .settings-main {
    position: relative;
    width: 100%;
    height: 100%;
    overflow: hidden;
    background: var(--bloom-surface-cream);
  }

  .settings-scroll-container {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    overflow-y: auto;
    padding: 8px 16px 24px;
  }

  .settings-inner {
    max-width: 1036px;
    margin: 0 auto;
  }

  .settings-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 24px;
    align-items: flex-start;
  }

  .grid-column {
    display: flex;
    flex-direction: column;
  }
</style>
