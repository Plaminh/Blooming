let offsetMs = 0;

export function recordServerDate(httpDate: string | null, clientNow = Date.now()): void {
  if (!httpDate) return;
  const serverTime = Date.parse(httpDate);
  if (Number.isFinite(serverTime)) offsetMs = serverTime - clientNow;
}

export function serverNow(clientNow = Date.now()): Date {
  return new Date(clientNow + offsetMs);
}
