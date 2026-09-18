import { readable } from 'svelte/store';

/** Current instant; consumers format it in the user's configured timezone. */
export const clockStore = readable(new Date(), (set) => {
  if (typeof window === 'undefined') return () => {};

  const now = new Date();
  set(now);

  const update = () => set(new Date());

  const delayToNextMinute = 60000 - (now.getSeconds() * 1000 + now.getMilliseconds());

  let intervalId: ReturnType<typeof setInterval> | undefined;
  const timeoutId: ReturnType<typeof setTimeout> = setTimeout(() => {
    update();
    intervalId = setInterval(update, 60000);
  }, delayToNextMinute);

  return () => {
    clearTimeout(timeoutId);
    if (intervalId !== undefined) {
      clearInterval(intervalId);
    }
  };
});
