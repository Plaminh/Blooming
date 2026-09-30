// @ts-nocheck -- a Node build script; the app's tsconfig has no Node types.
// Guard for the staging desktop build.
//
// A staging installer can only reach its API when two settings agree:
// PUBLIC_API_BASE_URL in .env.staging (where requests go) and connect-src in
// src-tauri/tauri.staging.conf.json (what the webview CSP allows). When they
// disagree every request, starting with registration, fails as a generic
// network error inside the installed app.
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');

export function readEnvValue(text, key) {
  for (const line of text.split(/\r?\n/)) {
    const match = line.match(/^\s*([A-Z0-9_]+)\s*=\s*(.*)\s*$/);
    if (match && match[1] === key) return match[2].replace(/^["']|["']$/g, '').trim();
  }
  return null;
}

export function connectSources(csp) {
  const directive = csp.split(';').map(part => part.trim()).find(part => part.startsWith('connect-src'));
  return directive ? directive.split(/\s+/).slice(1) : [];
}

export function checkStagingBuild(envText, tauriConfig) {
  const errors = [];
  const warnings = [];
  const apiUrl = readEnvValue(envText, 'PUBLIC_API_BASE_URL');
  if (!apiUrl) {
    errors.push('PUBLIC_API_BASE_URL is missing from .env.staging.');
    return { errors, warnings };
  }
  let origin;
  try {
    origin = new URL(apiUrl).origin;
  } catch {
    errors.push(`PUBLIC_API_BASE_URL is not a valid URL: ${apiUrl}`);
    return { errors, warnings };
  }
  const csp = tauriConfig?.app?.security?.csp;
  if (typeof csp === 'string' && !connectSources(csp).includes(origin)) {
    errors.push(
      `The staging CSP connect-src does not allow ${origin}. Add exactly that origin to ` +
      'src-tauri/tauri.staging.conf.json, otherwise the installed app cannot reach the API.'
    );
  }
  if (/^https?:\/\/(127\.0\.0\.1|localhost)(:|\/|$)/.test(apiUrl)) {
    warnings.push(
      `PUBLIC_API_BASE_URL points at ${origin}. That only works for local packaged testing; ` +
      'a hosted staging installer needs the HTTPS API origin.'
    );
  } else if (!apiUrl.startsWith('https://')) {
    warnings.push(`PUBLIC_API_BASE_URL should use HTTPS for hosted staging: ${apiUrl}`);
  }
  return { errors, warnings };
}

export function readStagingInputs() {
  return {
    envText: readFileSync(join(root, '.env.staging'), 'utf8'),
    tauriConfig: JSON.parse(readFileSync(join(root, 'src-tauri', 'tauri.staging.conf.json'), 'utf8')),
  };
}

if (process.argv[1] && fileURLToPath(import.meta.url) === process.argv[1]) {
  const { envText, tauriConfig } = readStagingInputs();
  const { errors, warnings } = checkStagingBuild(envText, tauriConfig);
  for (const warning of warnings) console.warn(`[staging-build] warning: ${warning}`);
  for (const error of errors) console.error(`[staging-build] error: ${error}`);
  if (errors.length) process.exit(1);
  console.log('[staging-build] API URL and CSP agree.');
}
