<script lang="ts">
  import type { AuthState } from '../../model/AuthState.svelte';
  import type { AuthMode, LoginSubmitData, RegisterSubmitData } from '../../types';
  import SegmentedTabButton from '../atoms/SegmentedTabButton.svelte';
  import LoginForm from './LoginForm.svelte';
  import RegistrationForm from './RegistrationForm.svelte';

  let { 
    state: authState,
    onSubmitLogin,
    onSubmitRegister,
    onModeChange,
    onResendVerification,
  }: { 
    state: AuthState;
    onSubmitLogin?: (data: LoginSubmitData) => void;
    onSubmitRegister?: (data: RegisterSubmitData) => void;
    onModeChange?: (mode: AuthMode) => void;
    onResendVerification?: (email: string) => void;
  } = $props();

  function switchMode(mode: AuthMode) {
    if (authState.mode === mode) return;
    authState.switchMode(mode);
    onModeChange?.(mode);
  }
</script>

<div class="auth-panel">
  <img
    class="welcome-leaf"
    src="/assets/icons/leaf-icon.png"
    alt=""
    width="90"
    height="90"
  />
  <div class="welcome-section">
    <h1 class="welcome-heading">Welcome to Blooming</h1>
    <p class="welcome-subtext">A brighter, more focused you.</p>
  </div>

  <div class="tabs-container" aria-label="Authentication modes">
    <SegmentedTabButton 
      label="LOGIN" 
      active={authState.mode === 'login'}
      onClick={() => switchMode('login')}
    />
    <SegmentedTabButton 
      label="REGISTER" 
      active={authState.mode === 'register'}
      onClick={() => switchMode('register')}
    />
  </div>

  <div class="form-container">
    {#if authState.errors.general}
      <div class="general-error" style="color: var(--bloom-color-alert); text-align: center; margin-bottom: 1rem; font-size: 14px;">
        {authState.errors.general}
      </div>
    {/if}
    {#if authState.isAwaitingVerification}
      <div class="verification-container" style="text-align: center; padding: 2rem 0;">
        <h2 style="font-size: 18px; color: var(--bloom-color-ink); margin-bottom: 1rem;">Check your email</h2>
        <p style="font-size: 14px; color: var(--bloom-color-ink-light); margin-bottom: 1.5rem;">
          {authState.emailDeliveryFailed ? 'A verification link could not be sent to' : 'We\'ve sent a verification link to'} <strong>{authState.email}</strong>.
        </p>
        <button 
          class="submit-button"
          disabled={authState.isLoading}
          onclick={() => {
            if (onResendVerification) {
               onResendVerification(authState.email);
            }
          }}
        >
          {authState.isLoading ? 'SENDING...' : 'RESEND VERIFICATION'}
        </button>
      </div>
    {:else}
      {#key authState.mode}
        <div class="auth-form-transition">
          {#if authState.mode === 'login'}
            <LoginForm state={authState} onSubmit={onSubmitLogin} onModeChange={() => switchMode('register')} />
          {:else}
            <RegistrationForm state={authState} onSubmit={onSubmitRegister} onModeChange={() => switchMode('login')} />
          {/if}
        </div>
      {/key}
    {/if}
  </div>
</div>
