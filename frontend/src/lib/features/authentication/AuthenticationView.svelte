<script lang="ts">
  import { createAuthState } from './model/AuthState.svelte';
  import type { LoginSubmitData, RegisterSubmitData, AuthCallbacks } from './types';
  import {
    desktopWindowService,
    type DesktopWindowService,
  } from '$lib/platform/desktopWindow';
  import DesktopAppShell from '$lib/shared/components/organisms/DesktopAppShell.svelte';
  import AuthenticationPanel from './components/organisms/AuthenticationPanel.svelte';
  import './styles/theme.css';

  let { 
    callbacks = {},
    windowService = desktopWindowService,
  }: { 
    callbacks?: AuthCallbacks;
    windowService?: DesktopWindowService;
  } = $props();

  const state = createAuthState();

  function handleLogin(data: LoginSubmitData) {
    if (callbacks.onSubmitLogin) {
      callbacks.onSubmitLogin(data);
    }
  }

  function handleRegister(data: RegisterSubmitData) {
    if (callbacks.onSubmitRegister) {
      callbacks.onSubmitRegister(data);
    }
  }
</script>

<DesktopAppShell
  variant="compact"
  showSidebar={false}
  {windowService}
  onTitleBarAction={(action) => callbacks.onTitleBarAction?.(action)}
>
  <div class="auth-view-container">
    <main class="auth-content-split">
      <div class="auth-illustration-col">
        <div class="illustration-wrapper">
          <img
            src="/assets/authentication/backgrounds/authentication-background.png"
            alt=""
            class="auth-bg-image"
          />
          <div class="marketing-copy">
            <p class="marketing-headline">Small steps enrich brighter days.</p>
            <hr class="marketing-separator" />
            <p class="marketing-subline">Plan today. A calmer tomorrow.</p>
          </div>
        </div>
      </div>

      <div class="auth-panel-col">
        <AuthenticationPanel
          {state}
          onSubmitLogin={handleLogin}
          onSubmitRegister={handleRegister}
          onModeChange={callbacks.onModeChange}
        />
      </div>
    </main>
  </div>
</DesktopAppShell>
