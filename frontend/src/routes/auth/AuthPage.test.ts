import { render, screen } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import { beforeEach, describe, expect, it, vi } from 'vitest';
import { APIError } from '$lib/api';
import { authStore } from '$lib/shared/stores/authStore';
import AuthPage from './+page.svelte';

vi.mock('$app/navigation', () => ({ goto: vi.fn() }));
vi.mock('$lib/shared/stores/authStore', () => ({
  authStore: {
    login: vi.fn(),
    register: vi.fn(),
    subscribe: vi.fn((cb) => {
      cb({ isAuthenticated: false, user: null });
      return () => {};
    }),
  },
}));

async function submitRegistration() {
  const user = userEvent.setup();
  const { container } = render(AuthPage);
  await user.click(screen.getByRole('button', { name: 'REGISTER', pressed: false }));
  await user.type(container.querySelector('#register-email') as HTMLInputElement, 'new@blooming.app');
  await user.type(container.querySelector('#register-password') as HTMLInputElement, 'Password123!');
  await user.type(container.querySelector('#register-confirm-password') as HTMLInputElement, 'Password123!');
  const form = screen.getByRole('form', { name: 'Register' });
  await user.click(form.querySelector('button[type="submit"]') as HTMLButtonElement);
}

describe('registration page', () => {
  beforeEach(() => vi.clearAllMocks());

  it('asks the user to check their email after a successful registration', async () => {
    vi.mocked(authStore.register).mockResolvedValueOnce(true);
    await submitRegistration();
    expect(await screen.findByText('Check your email')).toBeInTheDocument();
  });

  it('does not claim a second email was sent during the server cooldown', async () => {
    vi.mocked(authStore.register).mockResolvedValueOnce(true);
    await submitRegistration();
    await userEvent.click(screen.getByRole('button', { name: 'RESEND VERIFICATION' }));
    expect(await screen.findByText(/Please wait \d+s before resending/)).toBeInTheDocument();
  });

  it('leads an unverified re-registration to verification instead of a dead end', async () => {
    vi.mocked(authStore.register).mockRejectedValueOnce(new APIError(409, {
      detail: { code: 'EMAIL_NOT_VERIFIED', message: 'This email is registered but not verified yet.' },
    }));
    await submitRegistration();
    expect(await screen.findByText('Check your email')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'RESEND VERIFICATION' })).toBeInTheDocument();
  });

  it('still reports a verified duplicate email on the email field', async () => {
    vi.mocked(authStore.register).mockRejectedValueOnce(new APIError(409, { detail: 'Email already registered.' }));
    await submitRegistration();
    expect(await screen.findByText('Email already exists.')).toBeInTheDocument();
    expect(screen.queryByText('Check your email')).not.toBeInTheDocument();
  });
});
