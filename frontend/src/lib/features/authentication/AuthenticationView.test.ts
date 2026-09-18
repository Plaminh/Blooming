import { render, screen, within } from '@testing-library/svelte';
import userEvent from '@testing-library/user-event';
import axe from 'axe-core';
import { describe, expect, it, vi } from 'vitest';
import type { DesktopWindowService } from '$lib/platform/desktopWindow';
import AuthenticationView from './AuthenticationView.svelte';
import { authStore } from '$lib/shared/stores/authStore';
import { createAuthState } from './model/AuthState.svelte';

vi.mock('$lib/shared/stores/authStore', () => ({
  authStore: {
    login: vi.fn().mockResolvedValue(undefined),
    register: vi.fn().mockResolvedValue(undefined),
    isAuthenticated: false,
    subscribe: vi.fn((cb) => {
      cb({ isAuthenticated: false, user: null });
      return () => {};
    }),
  }
}));

function mockWindowService(): DesktopWindowService {
  return {
    openMainWindow: vi.fn().mockResolvedValue(undefined),
    minimizeCurrent: vi.fn().mockResolvedValue(undefined),
    toggleMaximizeCurrent: vi.fn().mockResolvedValue(false),
    isCurrentMaximized: vi.fn().mockResolvedValue(false),
    hideCurrent: vi.fn().mockResolvedValue(undefined),
    closeCurrent: vi.fn().mockResolvedValue(undefined),
    startDraggingCurrent: vi.fn().mockResolvedValue(undefined),
  };
}

function loginForm() {
  return screen.getByRole('form', { name: 'Login' });
}

function registerForm() {
  return screen.getByRole('form', { name: 'Register' });
}

async function switchToRegister(user = userEvent.setup()) {
  await user.click(screen.getByRole('button', { name: 'REGISTER', pressed: false }));
  return user;
}

describe('AuthenticationView', () => {
  it('shows the resend action when verification email delivery failed', async () => {
    const state = createAuthState();
    state.email = 'test@example.com';
    state.isAwaitingVerification = true;
    state.emailDeliveryFailed = true;
    const onResendVerification = vi.fn();

    render(AuthenticationView, { callbacks: { state, onResendVerification } });

    expect(screen.getByText(/A verification link could not be sent to/)).toBeInTheDocument();
    await userEvent.click(screen.getByRole('button', { name: 'RESEND VERIFICATION' }));
    expect(onResendVerification).toHaveBeenCalledWith('test@example.com');
  });

  it('renders only the default Login form and both segmented mode buttons', () => {
    const { container } = render(AuthenticationView);

    expect(screen.getByRole('heading', { name: 'Welcome to Blooming' })).toBeInTheDocument();
    expect(loginForm()).toBeInTheDocument();
    expect(screen.queryByRole('form', { name: 'Register' })).not.toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'LOGIN', pressed: true })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'REGISTER', pressed: false })).toBeInTheDocument();
    expect(screen.getByLabelText('Email')).toBeInTheDocument();
    expect(screen.getByLabelText('Password')).toBeInTheDocument();
    expect(screen.queryByLabelText('Confirm password')).not.toBeInTheDocument();
    expect(screen.getByLabelText('Remember me')).toHaveAttribute('type', 'checkbox');
    expect(screen.getByText('Small steps enrich brighter days.')).toBeInTheDocument();

    const imageSources = [...container.querySelectorAll('img')].map((image) => image.getAttribute('src'));
    expect(imageSources).toContain('/assets/authentication/backgrounds/authentication-background.png');
    expect(container.innerHTML).not.toContain('authentication-login.png');
  });

  it('renders Register and supports both bottom mode-switch controls', async () => {
    const user = userEvent.setup();
    render(AuthenticationView);

    await user.click(screen.getByRole('button', { name: 'Create an account' }));
    expect(registerForm()).toBeInTheDocument();
    expect(screen.queryByRole('form', { name: 'Login' })).not.toBeInTheDocument();
    expect(screen.getByLabelText('Confirm password')).toBeInTheDocument();
    expect(screen.queryByLabelText('Remember me')).not.toBeInTheDocument();

    await user.click(screen.getByRole('button', { name: 'Login' }));
    expect(loginForm()).toBeInTheDocument();
  });

  it('reports every retained mode change callback', async () => {
    const user = userEvent.setup();
    const onModeChange = vi.fn();
    render(AuthenticationView, { callbacks: { onModeChange } });

    await user.click(screen.getByRole('button', { name: 'REGISTER', pressed: false }));
    await user.click(screen.getByRole('button', { name: 'LOGIN', pressed: false }));
    await user.click(screen.getByRole('button', { name: 'Create an account' }));
    await user.click(screen.getByRole('button', { name: 'Login' }));

    expect(onModeChange.mock.calls.map(([mode]) => mode)).toEqual([
      'register',
      'login',
      'register',
      'login',
    ]);
  });

  it('uses native Remember-me behavior', async () => {
    const user = userEvent.setup();
    render(AuthenticationView);
    const checkbox = screen.getByLabelText('Remember me');

    expect(checkbox).not.toBeChecked();
    await user.click(checkbox);
    expect(checkbox).toBeChecked();
    checkbox.focus();
    await user.keyboard(' ');
    expect(checkbox).not.toBeChecked();
  });

  it('controls both registration password visibility buttons independently', async () => {
    const user = userEvent.setup();
    render(AuthenticationView);
    await switchToRegister(user);

    const password = screen.getByLabelText('Password') as HTMLInputElement;
    const confirmation = screen.getByLabelText('Confirm password') as HTMLInputElement;
    const toggles = screen.getAllByRole('button', { name: 'Show password' });

    await user.click(toggles[0]);
    expect(password.type).toBe('text');
    expect(confirmation.type).toBe('password');
    await user.click(toggles[1]);
    expect(password.type).toBe('text');
    expect(confirmation.type).toBe('text');
  });

  it('keeps invalid Login errors visible until each value is valid', async () => {
    const user = userEvent.setup();
    render(AuthenticationView);
    const form = loginForm();
    const email = within(form).getByLabelText('Email');
    const password = within(form).getByLabelText('Password');

    await user.click(within(form).getByRole('button', { name: 'LOGIN' }));
    expect(screen.getByText('Email is required')).toBeInTheDocument();
    expect(screen.getByText('Password is required')).toBeInTheDocument();
    expect(email).toHaveAttribute('aria-errormessage', 'login-email-error');

    await user.type(email, 'a');
    expect(screen.getByText('Invalid email format')).toBeInTheDocument();
    await user.type(password, 'short');
    expect(screen.getByText('Password must be at least 8 characters')).toBeInTheDocument();

    await user.type(email, '@example.com');
    await user.type(password, '123');
    expect(screen.queryByText('Invalid email format')).not.toBeInTheDocument();
    expect(screen.queryByText('Password must be at least 8 characters')).not.toBeInTheDocument();
    expect(email).not.toHaveAttribute('aria-invalid');
    expect(email).not.toHaveAttribute('aria-errormessage');
  });

  it('validates missing confirmation and revalidates it when either password changes', async () => {
    const user = userEvent.setup();
    render(AuthenticationView);
    await switchToRegister(user);
    const form = registerForm();
    const password = within(form).getByLabelText('Password');
    const confirmation = within(form).getByLabelText('Confirm password');

    await user.type(within(form).getByLabelText('Email'), 'test@example.com');
    await user.type(password, 'password123');
    await user.click(within(form).getByRole('button', { name: 'REGISTER' }));
    expect(screen.getByText('Confirm password is required')).toBeInTheDocument();

    await user.type(confirmation, 'password456');
    expect(screen.getByText('Passwords do not match')).toBeInTheDocument();
    await user.clear(confirmation);
    await user.type(confirmation, 'password123');
    expect(screen.queryByText('Passwords do not match')).not.toBeInTheDocument();

    await user.type(password, 'x');
    expect(screen.getByText('Passwords do not match')).toBeInTheDocument();
  });

  it('invokes Login only after the complete form is valid and preserves entered values', async () => {
    const user = userEvent.setup();
    const onSubmitLogin = vi.fn();
    render(AuthenticationView, { callbacks: { onSubmitLogin } });
    const form = loginForm();
    const email = within(form).getByLabelText('Email') as HTMLInputElement;

    await user.type(email, 'bad');
    await user.type(within(form).getByLabelText('Password'), 'password123');
    await user.click(within(form).getByRole('button', { name: 'LOGIN' }));
    expect(onSubmitLogin).not.toHaveBeenCalled();
    expect(email.value).toBe('bad');

    await user.clear(email);
    await user.type(email, 'test@example.com');
    await user.click(within(form).getByRole('button', { name: 'LOGIN' }));
    expect(onSubmitLogin).toHaveBeenCalledWith({
      email: 'test@example.com',
      password: 'password123',
      rememberMe: false,
    });
  });

  it('invokes Register only after valid input', async () => {
    const user = userEvent.setup();
    const onSubmitRegister = vi.fn();
    render(AuthenticationView, { callbacks: { onSubmitRegister } });
    await switchToRegister(user);
    const form = registerForm();

    // 1. Submit an invalid Register form.
    await user.click(within(form).getByRole('button', { name: 'REGISTER' }));
    
    // 2. Confirm onSubmitRegister was not called.
    expect(onSubmitRegister).not.toHaveBeenCalled();

    // 3. Enter valid values.
    await user.type(within(form).getByLabelText('Email'), 'test@example.com');
    await user.type(within(form).getByLabelText('Password'), 'password123');
    await user.type(within(form).getByLabelText('Confirm password'), 'password123');
    
    // 4. Submit again.
    await user.click(within(form).getByRole('button', { name: 'REGISTER' }));

    // 5. Confirm it was called exactly once with expected object.
    expect(onSubmitRegister).toHaveBeenCalledTimes(1);
    expect(onSubmitRegister).toHaveBeenCalledWith({
      email: 'test@example.com',
      password: 'password123',
    });
  });

  it('safely tolerates missing callbacks and prevents network requests', async () => {
    const fetchSpy = vi.spyOn(globalThis, 'fetch');
    const user = userEvent.setup();
    
    // 1. Renders Login without onSubmitLogin.
    render(AuthenticationView);
    
    // 2. Enters valid values and submits.
    const lForm = loginForm();
    await user.type(within(lForm).getByLabelText('Email'), 'test@example.com');
    await user.type(within(lForm).getByLabelText('Password'), 'password123');
    
    // 3. Confirms submission does not throw.
    await expect(async () => {
      await user.click(within(lForm).getByRole('button', { name: 'LOGIN' }));
    }).not.toThrow();

    // 4. Switches to Register without onSubmitRegister.
    await switchToRegister(user);
    const rForm = registerForm();

    // 5. Enters valid matching values and submits.
    await user.type(within(rForm).getByLabelText('Email'), 'test2@example.com');
    await user.type(within(rForm).getByLabelText('Password'), 'password123');
    await user.type(within(rForm).getByLabelText('Confirm password'), 'password123');
    
    // 6. Confirms submission does not throw.
    await expect(async () => {
      await user.click(within(rForm).getByRole('button', { name: 'REGISTER' }));
    }).not.toThrow();

    // 7. Confirms no network request occurred.
    expect(fetchSpy).not.toHaveBeenCalled();
    fetchSpy.mockRestore();
  });

  it('has no axe violations in Login, Register, or validation-error fixtures', async () => {
    const first = render(AuthenticationView);
    expect((await axe.run(first.container)).violations).toEqual([]);
    first.unmount();

    const second = render(AuthenticationView);
    await userEvent.click(screen.getByRole('button', { name: 'Create an account' }));
    expect((await axe.run(second.container)).violations).toEqual([]);
    await userEvent.click(within(registerForm()).getByRole('button', { name: 'REGISTER' }));
    expect((await axe.run(second.container)).violations).toEqual([]);
  });
});
