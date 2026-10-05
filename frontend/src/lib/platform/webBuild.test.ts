import { describe, expect, it } from 'vitest';
import { checkWebBuild } from '../../../scripts/check-web-build.mjs';

describe('hosted web build guard', () => {
  it('rejects the development loopback API URL for Vercel', () => {
    const errors = checkWebBuild({
      hosted: true,
      configuredApiUrl: 'http://127.0.0.1:8000/api/v1',
    });
    expect(errors[0]).toContain('hosted browser would call its own machine');
  });

  it('requires HTTPS for a hosted API', () => {
    expect(checkWebBuild({ hosted: true, configuredApiUrl: 'http://api.example.com/api/v1' })[0])
      .toContain('must use HTTPS');
  });

  it('requires exactly one /api/v1 prefix', () => {
    expect(checkWebBuild({ hosted: true, configuredApiUrl: 'https://api.example.com' })[0])
      .toContain('end with exactly /api/v1');
    expect(checkWebBuild({ hosted: true, configuredApiUrl: 'https://api.example.com/api/v1/api/v1' })[0])
      .toContain('end with exactly /api/v1');
  });

  it('accepts a public HTTPS API and leaves local builds unchanged', () => {
    expect(checkWebBuild({ hosted: true, configuredApiUrl: 'https://api.example.com/api/v1' }))
      .toEqual([]);
    expect(checkWebBuild({ hosted: true, configuredApiUrl: 'https://api.example.com/api/v1/' }))
      .toEqual([]);
    expect(checkWebBuild({ hosted: false, configuredApiUrl: 'http://127.0.0.1:8000/api/v1' }))
      .toEqual([]);
  });
});
