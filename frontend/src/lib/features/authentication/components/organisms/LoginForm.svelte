<script lang="ts">
  import type { AuthState } from '../../model/AuthState.svelte';
  import type { LoginSubmitData } from '../../types';
  import AuthenticationField from '../molecules/AuthenticationField.svelte';
  import PasswordField from '../molecules/PasswordField.svelte';
  import AuthenticationCheckbox from '../atoms/AuthenticationCheckbox.svelte';
  import ValidationMessage from '../molecules/ValidationMessage.svelte';

  let { 
    state,
    onSubmit,
    onModeChange,
  }: { 
    state: AuthState;
    onSubmit?: (data: LoginSubmitData) => void;
    onModeChange: () => void;
  } = $props();

  function handleSubmit(e: SubmitEvent) {
    e.preventDefault();
    if (state.validate()) {
      if (onSubmit) {
        onSubmit({
          email: state.email,
          password: state.password,
          rememberMe: state.rememberMe
        });
      }
    }
  }

  function handleEmailInput() {
    state.revalidateEmail();
  }

  function handlePasswordInput() {
    state.revalidatePassword();
  }
</script>

<form class="auth-form login-form" aria-label="Login" onsubmit={handleSubmit} novalidate>
  <div class="fields-container">
    <div class="field-group">
      <AuthenticationField 
        id="login-email"
        label="Email"
        bind:value={state.email}
        type="email"
        placeholder="you@example.com"
        iconName="email"
        invalid={!!state.errors.email}
        errorId="login-email-error"
        autocomplete="username"
        oninput={handleEmailInput}
      />
      <ValidationMessage id="login-email-error" message={state.errors.email} />
    </div>

    <div class="field-group">
      <PasswordField 
        id="login-password"
        label="Password"
        bind:value={state.password}
        placeholder="Your password"
        visible={state.passwordVisible}
        onToggleVisibility={() => state.togglePasswordVisibility()}
        invalid={!!state.errors.password}
        errorId="login-password-error"
        autocomplete="current-password"
        oninput={handlePasswordInput}
      />
      <ValidationMessage id="login-password-error" message={state.errors.password} />
    </div>

    <div class="remember-me-container">
      <AuthenticationCheckbox 
        label="Remember me"
        checked={state.rememberMe}
        onChange={(val) => state.rememberMe = val}
      />
    </div>
  </div>

  <div class="actions-container">
    <button type="submit" class="submit-button">
      LOGIN
    </button>
    
    <div class="prompt-container">
      <span class="prompt-text">Don't have an account?</span>
      <button 
        type="button" 
        class="mode-switch-button"
        onclick={onModeChange}
      >
        Create an account
      </button>
    </div>
  </div>
</form>
