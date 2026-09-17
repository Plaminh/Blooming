<script lang="ts">
  import { createAuthState } from './model/AuthState.svelte';
  import type { LoginSubmitData, RegisterSubmitData, AuthCallbacks } from './types';
  
  // Extend AuthCallbacks here or in types.ts
  interface ExtendedAuthCallbacks extends AuthCallbacks {
    onResendVerification?: (email: string) => void;
    state?: any;
  }
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
    callbacks?: ExtendedAuthCallbacks;
    windowService?: DesktopWindowService;
  } = $props();

  const defaultState = createAuthState();
  let state = $derived(callbacks.state || defaultState);

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
          onResendVerification={callbacks.onResendVerification}
        />
      </div>
    </main>
  </div>
</DesktopAppShell>
