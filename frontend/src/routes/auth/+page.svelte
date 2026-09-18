<script lang="ts">
  import AuthenticationView from '$lib/features/authentication/AuthenticationView.svelte';
  import { createAuthState } from '$lib/features/authentication/model/AuthState.svelte';
  import { api, APIError } from '$lib/api';
  import { authStore } from '$lib/shared/stores/authStore';
  import { goto } from '$app/navigation';
  import { onMount } from 'svelte';

  const state = createAuthState();
  let lastResend = 0;

  onMount(() => {
    if ($authStore.isAuthenticated) {
      // route to app if already authenticated
      goto('/today'); 
    }
  });

  async function handleLogin(data: any) {
    if (state.isLoading) return;
    state.isLoading = true;
    state.setFieldError('general', null);

    try {
      await authStore.login(data.email, data.password);
      goto('/today');
    } catch (error) {
      if (error instanceof APIError) {
        if (error.status === 401) {
          state.setFieldError('general', 'Invalid email or password.');
        } else if (error.status === 403 && error.detail?.detail === 'EMAIL_NOT_VERIFIED') {
          state.isAwaitingVerification = true;
        } else {
          state.setFieldError('general', error.message || 'An error occurred during login.');
        }
      } else {
        state.setFieldError('general', 'Network error. Please try again later.');
      }
    } finally {
      state.isLoading = false;
    }
  }

  async function handleRegister(data: any) {
    if (state.isLoading) return;
    state.isLoading = true;
    state.setFieldError('general', null);

    try {
      // Backend does not accept display_name in /register, it's set via settings
      await authStore.register(data.email, data.password);
      state.emailDeliveryFailed = false;
      state.isAwaitingVerification = true;
    } catch (error) {
      if (error instanceof APIError) {
        if (error.status === 409) {
          state.setFieldError('email', 'Email already exists.');
        } else if (error.status === 502 || error.status === 503) {
          // Registration is committed before the verification email is sent.
          state.emailDeliveryFailed = true;
          state.isAwaitingVerification = true;
          state.setFieldError('general', error.status === 503
            ? 'Account created, but email service configuration is invalid. Please contact the administrator.'
            : 'Account created, but the verification email could not be sent. Please try resending it.');
        } else {
          state.setFieldError('general', error.message || 'An error occurred during registration.');
        }
      } else {
        state.setFieldError('general', 'Network error. Please try again later.');
      }
    } finally {
      state.isLoading = false;
    }
  }

  async function handleResendVerification(email: string) {
    const now = Date.now();
    if (now - lastResend < 60000) {
      state.setFieldError('general', `Please wait ${Math.ceil((60000 - (now - lastResend)) / 1000)}s before resending.`);
      return;
    }

    state.isLoading = true;
    state.setFieldError('general', null);

    try {
      await api.post('/auth/resend-verification', { email });
      lastResend = Date.now();
      state.emailDeliveryFailed = false;
      state.setFieldError('general', 'Verification email sent successfully.');
    } catch (error) {
       if (error instanceof APIError) {
         state.setFieldError('general', error.message || 'Failed to resend verification email.');
       } else {
         state.setFieldError('general', 'Network error. Please try again later.');
       }
    } finally {
      state.isLoading = false;
    }
  }
</script>

<svelte:head>
  <title>Authentication - Blooming</title>
</svelte:head>

<AuthenticationView callbacks={{
  onSubmitLogin: handleLogin,
  onSubmitRegister: handleRegister,
  onResendVerification: handleResendVerification,
  state: state
}} />
