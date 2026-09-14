<script lang="ts">
  import DesktopTitleBar from '$lib/shared/components/organisms/DesktopTitleBar.svelte';
  import AppSidebar from '$lib/shared/components/organisms/AppSidebar.svelte';
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

<div class="settings-layout">
  <DesktopTitleBar />
  
  <div class="settings-content-wrapper">
    <AppSidebar activeRoute="SETTINGS" />
    
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
  </div>
</div>

<style>
  .settings-layout {
    display: flex;
    flex-direction: column;
    height: 100vh;
    width: 100vw;
    overflow: hidden;
    background-color: var(--bloom-background-cream, #fffbf0);
  }

  .settings-content-wrapper {
    display: flex;
    flex: 1;
    min-height: 0; /* Important for flex child scrolling */
  }

  .settings-main {
    flex: 1;
    position: relative;
  }

  .settings-scroll-container {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    overflow-y: auto;
    padding: 60px 80px;
  }

  .settings-inner {
    max-width: 1000px;
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
