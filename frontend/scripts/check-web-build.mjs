// @ts-nocheck -- a Node build script; the app tsconfig intentionally omits Node types.
// Prevent a hosted frontend from silently shipping the development loopback API URL.
import { existsSync, readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { readEnvValue } from './check-staging-build.mjs';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');

export function checkWebBuild({ hosted, configuredApiUrl }) {
  if (!hosted) return [];
  if (!configuredApiUrl) {
    return ['PUBLIC_API_BASE_URL must be configured for hosted builds.'];
  }
  let url;
  try {
    url = new URL(configuredApiUrl);
  } catch {
    return [`PUBLIC_API_BASE_URL is not a valid URL: ${configuredApiUrl}`];
  }
  if (url.hostname === '127.0.0.1' || url.hostname === 'localhost' || url.hostname === '::1') {
    return [
      `PUBLIC_API_BASE_URL points at ${url.origin}. A hosted browser would call its own machine; ` +
      'set the deployment environment variable to the public HTTPS backend URL.'
    ];
  }
  if (url.protocol !== 'https:') {
    return ['PUBLIC_API_BASE_URL must use HTTPS for a hosted build.'];
  }
  const apiPath = url.pathname.replace(/\/+$/, '');
  if (apiPath !== '/api/v1' || url.search || url.hash) {
    return [
      'PUBLIC_API_BASE_URL must end with exactly /api/v1 (for example, ' +
      'https://backend.example.com/api/v1).'
    ];
  }
  return [];
}

export function configuredApiUrl(environment = process.env) {
  if (environment.PUBLIC_API_BASE_URL) return environment.PUBLIC_API_BASE_URL;
  const localEnv = join(root, '.env');
  return existsSync(localEnv)
    ? readEnvValue(readFileSync(localEnv, 'utf8'), 'PUBLIC_API_BASE_URL')
    : null;
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  const hosted = process.env.VERCEL === '1' || process.env.BLOOMING_HOSTED_BUILD === '1';
  const errors = checkWebBuild({ hosted, configuredApiUrl: configuredApiUrl() });
  for (const error of errors) console.error(`[web-build] error: ${error}`);
  if (errors.length) process.exit(1);
}
