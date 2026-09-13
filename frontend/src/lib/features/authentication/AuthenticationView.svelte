<script lang="ts">
  import { createAuthState } from './model/AuthState.svelte';
  import type { LoginSubmitData, RegisterSubmitData, AuthCallbacks } from './types';
  import {
    desktopWindowService,
    type DesktopWindowService,
  } from '$lib/platform/desktopWindow';
  import AuthenticationTitleBar from './components/molecules/AuthenticationTitleBar.svelte';
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

<div class="auth-view-container">
  <AuthenticationTitleBar
    {windowService}
    onAction={(action) => callbacks.onTitleBarAction?.(action)}
  />

  <main class="auth-content-split">
    <!-- Left column: Illustration and marketing copy -->
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

    <!-- Right column: Interactive form panel -->
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
