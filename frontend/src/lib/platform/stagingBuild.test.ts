import { describe, expect, it } from 'vitest';
import { checkStagingBuild, readStagingInputs } from '../../../scripts/check-staging-build.mjs';

const csp = (connect: string) => ({ app: { security: { csp: `default-src 'self'; connect-src 'self' ${connect}` } } });

describe('staging build guard', () => {
  it('accepts an HTTPS API origin that the CSP allows', () => {
    const result = checkStagingBuild(
      'PUBLIC_API_BASE_URL=https://api.staging.example/api/v1',
      csp('https://api.staging.example')
    );
    expect(result).toEqual({ errors: [], warnings: [] });
  });

  it('fails when the CSP would block the configured API', () => {
    const result = checkStagingBuild(
      'PUBLIC_API_BASE_URL=https://api.staging.example/api/v1',
      csp('http://127.0.0.1:8000')
    );
    expect(result.errors[0]).toContain('does not allow https://api.staging.example');
  });

  it('warns when a staging build still targets the local backend', () => {
    const result = checkStagingBuild('PUBLIC_API_BASE_URL=http://127.0.0.1:8000/api/v1', csp('http://127.0.0.1:8000'));
    expect(result.errors).toEqual([]);
    expect(result.warnings[0]).toContain('local packaged testing');
  });

  it('fails without an API URL', () => {
    expect(checkStagingBuild('# nothing here', csp('https://x')).errors[0]).toContain('missing');
  });

  it('keeps the checked-in staging configuration consistent', () => {
    const { envText, tauriConfig } = readStagingInputs();
    expect(checkStagingBuild(envText, tauriConfig).errors).toEqual([]);
    // The staging installer must build the frontend in staging mode, or
    // .env.staging is ignored and the app targets the wrong API.
    expect(tauriConfig.build.beforeBuildCommand).toBe('npm run build:staging');
  });
});
