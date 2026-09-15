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
  }: { 
    state: AuthState;
    onSubmitLogin?: (data: LoginSubmitData) => void;
    onSubmitRegister?: (data: RegisterSubmitData) => void;
    onModeChange?: (mode: AuthMode) => void;
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
    {#key authState.mode}
      <div class="auth-form-transition">
        {#if authState.mode === 'login'}
          <LoginForm state={authState} onSubmit={onSubmitLogin} onModeChange={() => switchMode('register')} />
        {:else}
          <RegistrationForm state={authState} onSubmit={onSubmitRegister} onModeChange={() => switchMode('login')} />
        {/if}
      </div>
    {/key}
  </div>
</div>
