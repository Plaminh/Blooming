export function startTimeJumpDetector(
  onTimeJump: () => void,
  options: { intervalMs?: number; thresholdMs?: number } = {}
) {
  const intervalMs = options.intervalMs ?? 1_000;
  const thresholdMs = options.thresholdMs ?? 5_000;
  let previousTick = Date.now();
  const timer = window.setInterval(() => {
    const current = Date.now();
    if (current - previousTick > thresholdMs) onTimeJump();
    previousTick = current;
  }, intervalMs);
  return () => window.clearInterval(timer);
}
