import { describe, it, expect, vi, beforeEach } from 'vitest';
import { api, APIError, setAuthErrorHandler } from './api';

// Mock env variables
vi.mock('$env/static/public', () => ({
  PUBLIC_API_BASE_URL: 'http://127.0.0.1:8000/api/v1'
}));

const mockFetch = vi.fn();
vi.stubGlobal('fetch', mockFetch);

describe('api client', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.stubGlobal('localStorage', {
      getItem: vi.fn().mockReturnValue('test-token'),
      setItem: vi.fn(),
      removeItem: vi.fn()
    });
    setAuthErrorHandler(() => {});
  });

  it('strips redundant prefixes', async () => {
    mockFetch.mockResolvedValue({
      ok: true,
      status: 200,
      json: () => Promise.resolve({ success: true })
    });

    await api.get('/api/v1/me');
    expect(mockFetch).toHaveBeenCalledWith('http://127.0.0.1:8000/api/v1/me', expect.any(Object));

    await api.get('/api/garden');
    expect(mockFetch).toHaveBeenCalledWith('http://127.0.0.1:8000/api/v1/garden', expect.any(Object));

    await api.get('/v1/statistics');
    expect(mockFetch).toHaveBeenCalledWith('http://127.0.0.1:8000/api/v1/statistics', expect.any(Object));

    await api.get('/today');
    expect(mockFetch).toHaveBeenCalledWith('http://127.0.0.1:8000/api/v1/today', expect.any(Object));
    
    // Add tests for without trailing slashes, unrelated paths
    await api.get('/apiary');
    expect(mockFetch).toHaveBeenCalledWith('http://127.0.0.1:8000/api/v1/apiary', expect.any(Object));
  });

  it('normalizes Pydantic API errors', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 422,
      json: () => Promise.resolve({
        detail: [{ msg: 'Field required', loc: ['body', 'name'] }]
      })
    });

    try {
      await api.get('/test');
      expect.fail('Should have thrown APIError');
    } catch (e) {
      expect(e).toBeInstanceOf(APIError);
      expect((e as APIError).message).toBe('Field required');
      expect((e as APIError).status).toBe(422);
    }
  });

  it('triggers auth error handler on 401', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 401,
      json: () => Promise.resolve({ detail: 'Unauthorized' })
    });

    const handler = vi.fn();
    setAuthErrorHandler(handler);

    try {
      await api.get('/test');
    } catch (e) {
      // ignore
    }

    expect(handler).toHaveBeenCalled();
  });
  
  it('does not trigger auth error handler on 401 from /auth/login', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 401,
      json: () => Promise.resolve({ detail: 'Incorrect credentials' })
    });

    const handler = vi.fn();
    setAuthErrorHandler(handler);

    try {
      await api.post('/auth/login', { username: 'a', password: 'b' });
    } catch (e) {
      // ignore
    }

    expect(handler).not.toHaveBeenCalled();
  });

  it('passes AbortSignal to the underlying fetch', async () => {
    mockFetch.mockResolvedValueOnce({
      ok: true,
      status: 200,
      json: () => Promise.resolve({ success: true })
    });

    const controller = new AbortController();
    controller.abort();
    await api.get('/test', { signal: controller.signal });
    // The client wraps the caller's signal so it can also enforce a timeout;
    // aborting the caller's signal must still abort the underlying request.
    const passed = mockFetch.mock.calls[0][1].signal as AbortSignal;
    expect(passed).toBeInstanceOf(AbortSignal);
    expect(passed.aborted).toBe(true);
  });

  it('aborts a request that exceeds its timeout with a readable error', async () => {
    vi.useFakeTimers();
    try {
      mockFetch.mockImplementationOnce((_url: string, init: RequestInit) => new Promise((_resolve, reject) => {
        init.signal?.addEventListener('abort', () => reject(new DOMException('Aborted', 'AbortError')));
      }));
      const pending = api.get('/slow', { timeoutMs: 1000 });
      const assertion = expect(pending).rejects.toMatchObject({ status: 408 });
      await vi.advanceTimersByTimeAsync(1000);
      await assertion;
    } finally {
      vi.useRealTimers();
    }
  });
});
