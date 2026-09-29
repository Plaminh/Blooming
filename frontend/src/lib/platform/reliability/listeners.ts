import { startTimeJumpDetector } from './timeJump';

export function startReliabilityListeners(
  resync: () => void,
  recoverOnline: () => void,
): () => void {
  const periodic = window.setInterval(resync, 60_000);
  const stopTimeJumpDetector = startTimeJumpDetector(resync);
  const resyncWhenVisible = () => {
    if (!document.hidden) resync();
  };

  window.addEventListener('storage', resync);
  window.addEventListener('focus', resync);
  window.addEventListener('online', recoverOnline);
  document.addEventListener('visibilitychange', resyncWhenVisible);

  return () => {
    window.clearInterval(periodic);
    stopTimeJumpDetector();
    window.removeEventListener('storage', resync);
    window.removeEventListener('focus', resync);
    window.removeEventListener('online', recoverOnline);
    document.removeEventListener('visibilitychange', resyncWhenVisible);
  };
}
