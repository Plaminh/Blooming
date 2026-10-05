import { get } from 'svelte/store';
import { beforeEach, describe, expect, it, vi } from 'vitest';

const api = vi.hoisted(() => ({ get: vi.fn(), post: vi.fn() }));

vi.mock('$app/environment', () => ({ browser: true }));
vi.mock('$app/navigation', () => ({ goto: vi.fn() }));
vi.mock('$lib/api', () => ({
  api,
  APIError: class APIError extends Error {
    constructor(public status: number, public detail: unknown) {
      super('API error');
    }
  },
  setAuthErrorHandler: vi.fn(),
}));

describe('auth store contract', () => {
  beforeEach(() => {
    vi.resetModules();
    vi.clearAllMocks();
    localStorage.clear();
  });

  it('submits OAuth form fields, persists the token, and initializes the user', async () => {
    api.post.mockResolvedValue({ access_token: 'signed-token', token_type: 'bearer' });
    api.get.mockResolvedValue({ id: 'user-1', email: 'user@example.com', is_verified: true });
    const { authStore } = await import('./authStore');

    await expect(authStore.login('user@example.com', 'Password123!')).resolves.toBe(true);

    expect(api.post).toHaveBeenCalledWith(
      '/auth/login',
      { username: 'user@example.com', password: 'Password123!' },
      { formUrlEncoded: true },
    );
    expect(localStorage.getItem('blooming_access_token')).toBe('signed-token');
    expect(api.get).toHaveBeenCalledWith('/me');
    expect(get(authStore)).toMatchObject({
      token: 'signed-token',
      isAuthenticated: true,
      isInitialized: true,
      user: { email: 'user@example.com' },
    });
  });

  it('restores a persisted session on initialization', async () => {
    localStorage.setItem('blooming_access_token', 'persisted-token');
    api.get.mockResolvedValue({ id: 'user-1', email: 'user@example.com', is_verified: true });
    const { authStore } = await import('./authStore');

    await authStore.initialize();

    expect(api.get).toHaveBeenCalledWith('/me');
    expect(get(authStore)).toMatchObject({
      token: 'persisted-token',
      isAuthenticated: true,
      isInitialized: true,
    });
  });

  it('keeps the persisted session when the backend is unreachable', async () => {
    localStorage.setItem('blooming_access_token', 'persisted-token');
    api.get.mockRejectedValue(new TypeError('Failed to fetch'));
    const { authStore } = await import('./authStore');

    await authStore.initialize();

    expect(localStorage.getItem('blooming_access_token')).toBe('persisted-token');
    expect(get(authStore)).toMatchObject({ isAuthenticated: true, isInitialized: true });
  });

  it('keeps the persisted session on a server error', async () => {
    localStorage.setItem('blooming_access_token', 'persisted-token');
    const { APIError } = await import('$lib/api');
    api.get.mockRejectedValue(new APIError(503, 'down'));
    const { authStore } = await import('./authStore');

    await authStore.initialize();

    expect(localStorage.getItem('blooming_access_token')).toBe('persisted-token');
    expect(get(authStore).isInitialized).toBe(true);
  });

  it.each([401, 403])('drops the persisted session when /me returns %s', async (status) => {
    localStorage.setItem('blooming_access_token', 'rejected-token');
    const { APIError } = await import('$lib/api');
    api.get.mockRejectedValue(new APIError(status, 'rejected'));
    const { authStore } = await import('./authStore');

    await authStore.initialize();

    expect(localStorage.getItem('blooming_access_token')).toBeNull();
    expect(get(authStore)).toMatchObject({ isAuthenticated: false, isInitialized: true });
  });

  it('removes the persisted token on logout', async () => {
    localStorage.setItem('blooming_access_token', 'signed-token');
    const { authStore } = await import('./authStore');

    authStore.clearAuth();

    expect(localStorage.getItem('blooming_access_token')).toBeNull();
    expect(get(authStore)).toMatchObject({ token: null, isAuthenticated: false });
  });
});
