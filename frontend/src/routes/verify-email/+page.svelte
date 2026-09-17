<script lang="ts">
  import { onMount } from 'svelte';
  import { page } from '$app/stores';
  import { goto } from '$app/navigation';
  import DesktopAppShell from '$lib/shared/components/organisms/DesktopAppShell.svelte';
  import { api, APIError } from '$lib/api';
  import { authStore } from '$lib/shared/stores/authStore';

  let status = $state<'loading' | 'success' | 'error' | 'expired'>('loading');
  let errorMessage = $state('');

  onMount(async () => {
    const rawToken = $page.url.searchParams.get('token');
    if (!rawToken) {
      status = 'error';
      errorMessage = 'No verification token provided.';
      return;
    }

    try {
      const response = await api.post('/api/v1/auth/verify-email', { token: rawToken });

      if (response.access_token) {
        authStore.setToken(response.access_token);
        await authStore.initialize();
      }
      
      status = 'success';
      setTimeout(() => {
        goto('/garden-selection');
      }, 2000);
      
    } catch (e) {
      if (e instanceof APIError) {
        if (e.status === 400 && e.message === 'Invalid or expired token') {
          status = 'expired';
        } else {
          status = 'error';
          errorMessage = e.message || 'Failed to verify email.';
        }
      } else {
        status = 'error';
        errorMessage = 'Network error during verification.';
      }
    }
  });
</script>

<svelte:head>
  <title>Verify Email - Blooming</title>
</svelte:head>

<DesktopAppShell variant="compact" showSidebar={false}>
  <div class="verify-container">
    <div class="verify-card">
      {#if status === 'loading'}
        <h2>Verifying your email...</h2>
        <p>Please wait while we confirm your email address.</p>
      {:else if status === 'success'}
        <h2>Email Verified!</h2>
        <p>Your email has been successfully verified. Redirecting you to the app...</p>
      {:else if status === 'expired'}
        <h2>Link Expired</h2>
        <p>The verification link is invalid or has expired.</p>
        <a href="/auth" class="btn">Return to Login</a>
      {:else if status === 'error'}
        <h2>Verification Failed</h2>
        <p>{errorMessage}</p>
        <a href="/auth" class="btn">Return to Login</a>
      {/if}
    </div>
  </div>
</DesktopAppShell>

<style>
  .verify-container {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background-color: var(--bloom-surface-cream);
  }
  .verify-card {
    background: white;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    text-align: center;
    max-width: 400px;
    width: 100%;
  }
  h2 {
    margin-bottom: 1rem;
    color: var(--bloom-color-ink);
  }
  p {
    margin-bottom: 1.5rem;
    color: var(--bloom-color-ink-light);
  }
  .btn {
    display: inline-block;
    padding: 0.5rem 1rem;
    background-color: var(--bloom-color-primary);
    color: white;
    text-decoration: none;
    border-radius: 4px;
    font-weight: 500;
  }
  .btn:hover {
    opacity: 0.9;
  }
</style>
