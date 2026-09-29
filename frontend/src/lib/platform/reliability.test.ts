import { get } from 'svelte/store';
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest';
import {
  FOCUS_FINISH_QUEUE_KEY,
  createResync,
  enqueueFocusFinish,
  flushFocusFinishQueue,
  startTimeJumpDetector,
  startReliabilityListeners,
  synchronizeAuthenticatedStartup
} from './reliability';

describe('desktop reliability', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    localStorage.clear();
  });
  afterEach(() => vi.useRealTimers());

  it('coalesces overlapping resync requests and records successful sync time', async () => {
    let release!: () => void;
    const pending = new Promise<void>(resolve => { release = resolve; });
    const dependencies = {
      fetchSession: vi.fn(() => pending),
      fetchReminders: vi.fn(async () => undefined),
      refreshPlant: vi.fn(async () => undefined)
    };
    const sync = createResync(dependencies);
    const first = sync.resync();
    const second = sync.resync();
    expect(first).toBe(second);
    expect(dependencies.fetchSession).toHaveBeenCalledTimes(1);
    release();
    await first;
    expect(get(sync.freshness).lastSyncedAt).toBe(Date.now());
  });

  it('detects a large time jump but ignores normal scheduling delay', () => {
    const jumped = vi.fn();
    const stop = startTimeJumpDetector(jumped);
    vi.advanceTimersByTime(5_000);
    expect(jumped).not.toHaveBeenCalled();
    vi.setSystemTime(Date.now() + 6_001);
    vi.advanceTimersByTime(1_000);
    expect(jumped).toHaveBeenCalledTimes(1);
    stop();
  });

  it('deduplicates queued focus finishes and removes only successful sends', async () => {
    const item = { run_id: 'run-1', outcome: 'DONE', should_replan: true };
    enqueueFocusFinish(localStorage, item);
    enqueueFocusFinish(localStorage, item);
    enqueueFocusFinish(localStorage, { ...item, run_id: 'run-2' });
    expect(JSON.parse(localStorage.getItem(FOCUS_FINISH_QUEUE_KEY)!)).toHaveLength(2);
    const send = vi.fn(async value => {
      if (value.run_id === 'run-2') throw new TypeError('offline');
    });
    const remaining = await flushFocusFinishQueue(localStorage, send);
    expect(remaining.map(value => value.run_id)).toEqual(['run-2']);
    expect(send).toHaveBeenCalledTimes(2);
  });

  it('removes permanent HTTP failures instead of retrying forever', async () => {
    enqueueFocusFinish(localStorage, { run_id: 'bad-run', outcome: 'DONE', should_replan: true });
    const permanent = vi.fn();
    const remaining = await flushFocusFinishQueue(
      localStorage,
      async () => { throw { status: 422 }; },
      permanent,
    );
    expect(remaining).toEqual([]);
    expect(permanent).toHaveBeenCalledWith(expect.objectContaining({ run_id: 'bad-run' }), { status: 422 });
  });

  it('keeps timeout and backend-unavailable failures queued', async () => {
    enqueueFocusFinish(localStorage, { run_id: 'timeout', outcome: 'DONE', should_replan: true });
    const remaining = await flushFocusFinishQueue(localStorage, async () => { throw { status: 503 }; });
    expect(remaining.map(item => item.run_id)).toEqual(['timeout']);
  });

  it('does not flush authenticated writes during unauthenticated startup', async () => {
    const flush = vi.fn(async () => undefined);
    const resync = vi.fn(async () => undefined);
    await synchronizeAuthenticatedStartup(false, flush, resync);
    expect(flush).not.toHaveBeenCalled();
    expect(resync).not.toHaveBeenCalled();
  });

  it('routes browser reliability triggers through the supplied resync path', () => {
    const resync = vi.fn();
    const online = vi.fn();
    const stop = startReliabilityListeners(resync, online);
    window.dispatchEvent(new Event('focus'));
    window.dispatchEvent(new Event('storage'));
    window.dispatchEvent(new Event('online'));
    expect(resync).toHaveBeenCalledTimes(2);
    expect(online).toHaveBeenCalledTimes(1);
    stop();
  });
});
