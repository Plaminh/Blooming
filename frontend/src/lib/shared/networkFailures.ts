export function httpErrorStatus(error: unknown): number | null {
  if (!error || typeof error !== 'object' || !('status' in error)) return null;
  return typeof error.status === 'number' ? error.status : null;
}

export function isNetworkFailure(error: unknown): boolean {
  return error instanceof TypeError;
}

export function isRetryableTransportFailure(error: unknown): boolean {
  const status = httpErrorStatus(error);
  return isNetworkFailure(error) || status === 408 || (status !== null && status >= 500);
}
