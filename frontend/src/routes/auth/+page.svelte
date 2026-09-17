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
    state.isLoading = true;
    state.setFieldError('general', null);

    try {
      const response = await api.post('/api/v1/auth/login', {
        username: data.email,
        password: data.password
      }, { formUrlEncoded: true });

      // Save JWT
      authStore.setToken(response.access_token);
      
      // Fetch user data
      await authStore.initialize();
      
      // Navigate to app. Let's see what the onboarding route is, or default to '/today'
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
    state.isLoading = true;
    state.setFieldError('general', null);

    try {
      await api.post('/api/v1/auth/register', {
        email: data.email,
        password: data.password,
        display_name: data.email.split('@')[0] // Basic display name
      });
      
      // 201: show check your email
      state.isAwaitingVerification = true;

    } catch (error) {
      if (error instanceof APIError) {
        if (error.status === 409) {
          state.setFieldError('email', 'Email already exists.');
        } else if (error.status === 502 || error.status === 503) {
          state.setFieldError('general', 'Email service is currently unavailable.');
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
      await api.post('/api/v1/auth/resend-verification', { email });
      lastResend = Date.now();
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
