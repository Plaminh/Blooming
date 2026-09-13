<script lang="ts">
  import type { AuthState } from '../../model/AuthState.svelte';
  import type { RegisterSubmitData } from '../../types';
  import AuthenticationField from '../molecules/AuthenticationField.svelte';
  import PasswordField from '../molecules/PasswordField.svelte';
  import ValidationMessage from '../molecules/ValidationMessage.svelte';

  let { 
    state,
    onSubmit,
    onModeChange,
  }: { 
    state: AuthState;
    onSubmit?: (data: RegisterSubmitData) => void;
    onModeChange: () => void;
  } = $props();

  function handleSubmit(e: SubmitEvent) {
    e.preventDefault();
    if (state.validate()) {
      if (onSubmit) {
        onSubmit({
          email: state.email,
          password: state.password
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

  function handleConfirmPasswordInput() {
    state.revalidateConfirmPassword();
  }
</script>

<form class="auth-form register-form" aria-label="Register" onsubmit={handleSubmit} novalidate>
  <div class="fields-container">
    <div class="field-group">
      <AuthenticationField 
        id="register-email"
        label="Email"
        bind:value={state.email}
        type="email"
        placeholder="you@example.com"
        iconName="email"
        invalid={!!state.errors.email}
        errorId="register-email-error"
        autocomplete="username"
        oninput={handleEmailInput}
      />
      <ValidationMessage id="register-email-error" message={state.errors.email} />
    </div>

    <div class="field-group">
      <PasswordField 
        id="register-password"
        label="Password"
        bind:value={state.password}
        placeholder="Your password"
        visible={state.passwordVisible}
        onToggleVisibility={() => state.togglePasswordVisibility()}
        invalid={!!state.errors.password}
        errorId="register-password-error"
        autocomplete="new-password"
        oninput={handlePasswordInput}
      />
      <ValidationMessage id="register-password-error" message={state.errors.password} />
    </div>

    <div class="field-group">
      <PasswordField 
        id="register-confirm-password"
        label="Confirm password"
        bind:value={state.confirmPassword}
        placeholder="Your password"
        visible={state.confirmPasswordVisible}
        onToggleVisibility={() => state.toggleConfirmPasswordVisibility()}
        invalid={!!state.errors.confirmPassword}
        errorId="register-confirm-error"
        autocomplete="new-password"
        oninput={handleConfirmPasswordInput}
      />
      <ValidationMessage id="register-confirm-error" message={state.errors.confirmPassword} />
    </div>
  </div>

  <div class="actions-container">
    <button type="submit" class="submit-button">
      REGISTER
    </button>
    
    <div class="prompt-container">
      <span class="prompt-text">Already have an account?</span>
      <button 
        type="button" 
        class="mode-switch-button"
        onclick={onModeChange}
      >
        Login
      </button>
    </div>
  </div>
</form>
